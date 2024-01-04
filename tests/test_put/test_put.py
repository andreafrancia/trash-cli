import os
from typing import List
from typing import Optional

import flexmock
from six import StringIO

from tests.support.fake_is_mount import FakeIsMount
from tests.test_put.support.dummy_clock import FixedClock
from tests.test_put.support.dummy_clock import jan_1st_2024
from tests.test_put.support.fake_fs.failing_fake_fs import FailingFakeFs
from tests.test_put.support.fake_random import FakeRandomInt
from tests.test_put.test_put_command.recording_backend import RecordingBackend
from tests.test_put.test_put_command.result import Result
from trashcli.fstab.volume_of import VolumeOfImpl
from trashcli.lib.environ import Environ
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.lib.exit_codes import EX_OK
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.core.logs import LogTag
from trashcli.put.main import make_cmd
from trashcli.put.parser import ensure_int


class TestPut:
    def setup_method(self):
        self.fs = FailingFakeFs()
        self.user_input = HardCodedInput('y')
        self.randint = FakeRandomInt([])
        self.is_mount = FakeIsMount(['/'])

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

    def test_when_a_trashinfo_file_already_exists(self):
        def touch_and_trash(path):
            self.fs.touch(path)
            self.run_cmd(['trash-put', path])

        touch_and_trash("/foo")
        touch_and_trash("/foo")
        touch_and_trash("/foo")

        assert self.fs.ls_aa('/.Trash-123/info') == [
            'foo.trashinfo',
            'foo_1.trashinfo',
            'foo_2.trashinfo'
        ]

    def test_when_moving_file_in_trash_dir_fails(self):
        self.fs.touch("foo")
        self.fs.fail_move_on("/foo")

        result = self.run_cmd(['trash-put', '-v', '/foo'])

        assert result.exit_code_and_stderr() == [EX_IOERR, [
            "trash-put: cannot trash regular empty file '/foo' (from volume '/')",
            'trash-put:  `- failed to trash /foo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
            'trash-put:  `- failed to trash /foo in /.Trash-123, because failed to move /foo in /.Trash-123/files: move failed']]

    def test_should_not_trash_dot_entry(self):
        result = self.run_cmd(['trash-put', '.'])

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            ["trash-put: cannot trash directory '.'"]]

    def test_should_not_trash_dot_dot_entry(self):
        result = self.run_cmd(['trash-put', '..'])

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            ["trash-put: cannot trash directory '..'"]]

    def test_user_reply_no(self):
        self.fs.touch("foo")
        self.user_input.set_reply('n')

        result = self.run_cmd(['trash-put', '-i', 'foo'])

        assert result.exit_code_and_stderr() + [self.user_input.last_prompt(),
                                                self.fs.ls_existing(["foo"])] == [
                   EX_OK, [], "trash-put: trash regular empty file 'foo'? ",
                   ['foo'],
               ]

    def test_user_reply_yes(self):
        self.fs.touch("foo")
        self.user_input.set_reply('y')

        result = self.run_cmd(['trash-put', '-i', 'foo'])

        assert result.exit_code_and_stderr() + [self.user_input.last_prompt(),
                                                self.fs.ls_existing(["foo"])] == [
                   EX_OK, [], "trash-put: trash regular empty file 'foo'? ",
                   []
               ]

    def test_when_file_does_not_exist(self):
        result = self.run_cmd(['trash-put', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            ["trash-put: cannot trash non existent 'non-existent'"]]

    def test_when_file_does_not_exist_with_force(self):
        result = self.run_cmd(['trash-put', '-f', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result.exit_code_and_stderr() == [EX_OK, []]

    def test_put_does_not_try_to_trash_non_existing_file(self):
        result = self.run_cmd(['trash-put', '-vvv', 'non-existing'],
                              {"HOME": "/home/user"}, 123)

        assert result.exit_code_and_stderr() == \
               [
                   EX_IOERR,
                   ["trash-put: cannot trash non existent 'non-existing'"]
               ]

    def test_when_file_cannot_be_trashed(self):
        self.fs.touch("foo")
        self.fs.fail_move_on("foo")

        result = self.run_cmd(['trash-put', 'foo'])

        assert (result.exit_code_and_logs(LogTag.trash_failed) ==
                (74, [
                    "cannot trash regular empty file 'foo' (from volume '/')"]))

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

        result = self.run_cmd(['trash-put', '-v', 'pippo'], {}, 123)

        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            [
                "trash-put: cannot trash regular empty file 'pippo' (from volume '/')",
                'trash-put:  `- failed to trash pippo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
                "trash-put:  `- failed to trash pippo in /.Trash-123, because error during directory creation: [Errno 13] Permission denied: '/.Trash-123/files'"
            ]
        ]

    def test_multiple_volumes(self):
        self.fs.makedirs('/disk1', 0o700)
        self.fs.makedirs('/disk1/.Trash-123', 0o000)
        self.fs.make_file("/disk1/pippo")
        self.is_mount.add_mount_point('/disk1')

        result = self.run_cmd(['trash-put', '-v', '--home-fallback',
                               '/disk1/pippo'],
                              {'HOME': '/home/user'}, 123)

        assert result.stderr == ["trash-put: cannot trash regular empty file '/disk1/pippo' (from volume '/disk1')",
                                 'trash-put:  `- failed to trash /disk1/pippo in /home/user/.local/share/Trash, because trash dir and file to be trashed are not in the same volume, trash-dir volume: /, file volume: /disk1',
                                 'trash-put:  `- failed to trash /disk1/pippo in /disk1/.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /disk1/.Trash/123, parent: /disk1/.Trash',
                                 "trash-put:  `- failed to trash /disk1/pippo in /disk1/.Trash-123, because error during directory creation: [Errno 13] Permission denied: '/disk1/.Trash-123/files'",
                                 'trash-put:  `- failed to trash /disk1/pippo in /home/user/.local/share/Trash, because home fallback not enabled']

    def test_when_it_fails_to_prepare_trash_info_data(self):
        flexmock.flexmock(self.fs).should_receive('parent_realpath2'). \
            and_raise(IOError, 'Corruption')
        self.fs.make_file("foo")

        result = self.run_cmd(['trash-put', '-v', 'foo'],
                              {"HOME": "/home/user"}, 123)
        assert result.exit_code_and_stderr() == [
            EX_IOERR,
            ["trash-put: cannot trash regular empty file 'foo' (from volume '/')",
             'trash-put:  `- failed to trash foo in /home/user/.local/share/Trash, because failed to generate trashinfo content: Corruption',
             'trash-put:  `- failed to trash foo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
             'trash-put:  `- failed to trash foo in /.Trash-123, because failed to generate trashinfo content: Corruption']]

    def test_make_file(self):
        self.fs.make_file("pippo", 'content')
        assert True == self.fs.exists("pippo")

    def test_when_file_exists(self):
        self.fs.make_file("pippo", 'content')

        result = self.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        actual = {
            'file_pippo_exists': self.fs.exists("pippo"),
            'exit_code': result.exit_code,
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
            'exit_code': result.exit_code,
            'stderr': result.stderr,
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
                              "trash-put: cannot trash regular file 'pippo' (from volume '/')",
                              'trash-put:  `- failed to trash pippo in /home/user/.local/share/Trash, because failed to move pippo in /home/user/.local/share/Trash/files: No space left on device',
                              'trash-put:  `- failed to trash pippo in /.Trash/123, because trash dir cannot be created because its parent does not exists, trash-dir: /.Trash/123, parent: /.Trash',
                              'trash-put:  `- failed to trash pippo in /.Trash-123, because failed to move pippo in /.Trash-123/files: No space left on device'],
                          'file_pippo_exists': True,
                          'files_in_files_dir': [],
                          'files_in_info_dir': []}

    def test_when_a_error_during_move(self):
        self.fs.make_file("pippo", 'content')

        result = self.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        assert False == self.fs.exists("pippo")
        assert EX_OK == result.exit_code
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
        stderr = StringIO()
        clock = FixedClock(jan_1st_2024())
        volumes = VolumeOfImpl(self.is_mount, os.path.normpath)
        backend = RecordingBackend(stderr)
        cmd = make_cmd(clock=clock,
                       fs=self.fs,
                       user_input=self.user_input,
                       randint=self.randint,
                       backend=backend,
                       volumes=volumes)
        try:
            exit_code = cmd.run_put(args, environ, uid)
        except IOError as e:
            err = e
        stderr_lines = stderr.getvalue().splitlines()

        return Result(stderr_lines, str(err), ensure_int(exit_code),
                      backend.collected())
