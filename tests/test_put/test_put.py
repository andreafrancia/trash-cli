import os
import unittest
from typing import Optional, NamedTuple, List

import flexmock
from six import StringIO

from tests.support.fake_is_mount import FakeIsMount
from tests.test_put.support.dummy_clock import FixedClock, jan_1st_2024
from tests.test_put.support.fake_fs.failing_fake_fs import FailingFakeFs
from tests.test_put.support.fake_random import FakeRandomInt
from trashcli.fstab.volume_of import VolumeOfImpl
from trashcli.lib.exit_codes import EX_OK, EX_IOERR
from trashcli.lib.my_input import HardCodedInput
from trashcli.lib.environ import Environ
from trashcli.put.main import make_cmd
from trashcli.put.parser import ensure_int


class TestPut(unittest.TestCase):
    def setUp(self):
        self.fs = FailingFakeFs()
        self.my_input = HardCodedInput('y')
        self.randint = FakeRandomInt(1492)
        self.is_mount = FakeIsMount(['/'])
        self.volumes = VolumeOfImpl(self.is_mount, os.path.normpath)
        self.stderr = StringIO()
        self.clock = FixedClock(jan_1st_2024())
        self.cmd = make_cmd(clock=self.clock,
                            fs=self.fs,
                            user_input=self.my_input,
                            randint=self.randint,
                            stderr=self.stderr,
                            volumes=self.volumes)

    def test_when_needs_a_different_suffix(self):
        self.fs.touch("/foo")
        self.fs.fail_atomic_create_unless("foo_1.trashinfo")

        self.run_cmd(['trash-put', '/foo'])

        assert self.fs.ls_aa('/.Trash-123/files') == ['foo_1']

    def test_when_needs_a_random_suffix(self):
        self.fs.touch("/foo")
        self.fs.fail_atomic_create_unless("foo_123.trashinfo")
        self.randint.set_reply(123)

        self.run_cmd(['trash-put', '/foo'])

        assert self.fs.ls_aa('/.Trash-123/files') == ['foo_123']

    def test_when_file_does_not_exist(self):
        result = self.run_cmd(['trash-put', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result.all() == [
            EX_IOERR,
            ["trash-put: cannot trash non existent 'non-existent'"]]

    def test_when_file_does_not_exist_with_force(self):
        result = self.run_cmd(['trash-put', '-f', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result.all() == [EX_OK, []]

    def test_put_does_not_try_to_trash_non_existing_file(self):
        result = self.run_cmd(['trash-put', '-vvv', 'non-existing'],
                              {"HOME": "/home/user"}, 123)

        assert result.all() == \
               [
                   EX_IOERR,
                   ["trash-put: cannot trash non existent 'non-existing'"]
               ]

    def test_exit_code_will_be_0_when_trash_succeeds(self):
        self.fs.touch("pippo")

        result = self.run_cmd(['trash-put', 'pippo'])

        assert result.exit_code == EX_OK

    def test_exit_code_will_be_non_0_when_trash_fails(self):
        self.fs.assert_does_not_exist("a")

        result = self.run_cmd(['trash-put', 'a'])

        assert result.exit_code == EX_IOERR

    def test_exit_code_will_be_non_0_when_just_one_trash_fails(self):
        self.fs.touch("a")
        self.fs.assert_does_not_exist("b")
        self.fs.touch("c")

        result = self.run_cmd(['trash-put', 'a', 'b', 'c'])

        assert result.exit_code == EX_IOERR

    def test_when_there_is_no_working_trash_dir(self):
        self.fs.make_file("pippo")
        self.fs.makedirs('/.Trash-123', 0o000)

        result = self.run_cmd(['trash-put', '-vvv', 'pippo'], {}, 123)

        assert result.all() == [
            EX_IOERR,
            [
                'trash-put: volume of file: /',
                'trash-put: found unusable .Trash dir (should be a dir): /.Trash',
                'trash-put: trash directory is not secure: /.Trash/123',
                'trash-put: trying trash dir: /.Trash-123 from volume: /',
                "trash-put: failed to trash pippo in /.Trash-123, because: [Errno 13] Permission denied: '/.Trash-123/files'",
                "trash-put: cannot trash regular empty file 'pippo'",
            ]
        ]

    def test_multiple_volumes(self):
        self.fs.makedirs('/disk1', 0o700)
        self.fs.makedirs('/disk1/.Trash-123', 0o000)
        self.fs.make_file("/disk1/pippo")
        self.is_mount.add_mount_point('/disk1')

        result = self.run_cmd(['trash-put', '-vvv', '--home-fallback',
                               '/disk1/pippo'],
                              {'HOME': '/home/user'}, 123)

        assert result[0] == ['trash-put: volume of file: /disk1',
                             'trash-put: trying trash dir: /home/user/.local/share/Trash from volume: /',
                             "trash-put: won't use trash dir ~/.local/share/Trash because its volume (/) in a different volume than /disk1/pippo (/disk1)",
                             'trash-put: found unusable .Trash dir (should be a dir): /disk1/.Trash',
                             'trash-put: trash directory is not secure: /disk1/.Trash/123',
                             'trash-put: trying trash dir: /disk1/.Trash-123 from volume: /disk1',
                             "trash-put: failed to trash /disk1/pippo in /disk1/.Trash-123, because: [Errno 13] Permission denied: '/disk1/.Trash-123/files'",
                             'trash-put: trying trash dir: /home/user/.local/share/Trash from volume: /',
                             "trash-put: trash dir not enabled: ~/.local/share/Trash",
                             "trash-put: cannot trash regular empty file '/disk1/pippo'"]

    def test_make_file(self):
        self.fs.make_file("pippo", 'content')
        assert True == self.fs.exists("pippo")

    def test_when_file_exists(self):
        self.fs.make_file("pippo", 'content')

        result = self.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        actual = {
            'file_pippo_exists': self.fs.exists("pippo"),
            'exit_code': result[2],
            'files_in_info_dir': self.fs.ls_aa(
                '/home/user/.local/share/Trash/info'),
            "content_of_trashinfo": self.fs.read(
                '/home/user/.local/share/Trash/info/pippo.trashinfo'
            ).decode('utf-8'),
            'files_in_files_dir': self.fs.ls_aa(
                '/home/user/.local/share/Trash/files'),
            "content_of_trashed_file": self.fs.read(
                '/home/user/.local/share/Trash/files/pippo'),
        }
        assert actual == {'content_of_trashed_file': 'content',
                          'content_of_trashinfo': '[Trash Info]\nPath=/pippo\nDeletionDate=2014-01-01T00:00:00\n',
                          'exit_code': 0,
                          'file_pippo_exists': False,
                          'files_in_files_dir': ['pippo'],
                          'files_in_info_dir': ['pippo.trashinfo']}

    def test_when_file_move_fails(self):
        flexmock.flexmock(self.fs).should_receive('move'). \
            and_raise(IOError, 'No space left on device')
        self.fs.make_file("pippo", 'content')

        result = self.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        actual = {
            'file_pippo_exists': self.fs.exists("pippo"),
            'exit_code': result[2],
            'stderr': result[0],
            'files_in_info_dir': self.fs.ls_aa(
                '/home/user/.local/share/Trash/info'),
            "content_of_trashinfo": self.fs.read_null(
                '/home/user/.local/share/Trash/info/pippo.trashinfo'),
            'files_in_files_dir': self.fs.ls_aa(
                '/home/user/.local/share/Trash/files'),
            "content_of_trashed_file": self.fs.read_null(
                '/home/user/.local/share/Trash/files/pippo'),
        }
        assert actual == {'content_of_trashed_file': None,
                          'content_of_trashinfo': None,
                          'exit_code': EX_IOERR,
                          'stderr': [
                              "trash-put: cannot trash regular file 'pippo'"],
                          'file_pippo_exists': True,
                          'files_in_files_dir': [],
                          'files_in_info_dir': []}

    def test_when_a_error_during_move(self):
        self.fs.make_file("pippo", 'content')

        result = self.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        assert False == self.fs.exists("pippo")
        assert EX_OK == result[2]
        assert ['pippo.trashinfo'] == self.fs.ls_aa(
            '/home/user/.local/share/Trash/info')
        trash_info = self.fs.read(
            '/home/user/.local/share/Trash/info/pippo.trashinfo'
        ).decode('utf-8')
        assert trash_info == '[Trash Info]\nPath=/pippo\nDeletionDate=2014-01-01T00:00:00\n'
        assert ['pippo'] == self.fs.ls_aa(
            '/home/user/.local/share/Trash/files')
        assert self.fs.read('/home/user/.local/share/Trash/files/pippo') \
               == 'content'

    def run_cmd(self,
                args,  # type: List[str]
                environ=None,  # type: Optional[Environ]
                uid=None,  # type: Optional[int]
                ):  # type: (...) -> Result
        environ = environ or {}
        uid = uid or 123
        err = None
        exit_code = None
        try:
            exit_code = self.cmd.run_put(args, environ, uid)
        except IOError as e:
            err = e
        stderr = self.stderr.getvalue().splitlines()

        return Result(stderr, str(err), ensure_int(exit_code))


class Result(NamedTuple('Result', [
    ('stderr', List[str]),
    ('err', str),
    ('exit_code', int),
])):
    def all(self):
        return [self.exit_code, self.stderr]
