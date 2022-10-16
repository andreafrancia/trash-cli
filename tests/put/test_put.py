import datetime
import unittest

from flexmock import Mock
from six import StringIO

from tests.put.support.dummy_clock import DummyClock
from tests.put.support.fake_fs.fake_fs import FakeFs
from trashcli.fstab import create_fake_volume_of
from trashcli.put.main import make_cmd
from trashcli.trash import EX_IOERR, EX_OK


class TestPut(unittest.TestCase):
    def setUp(self):
        clock = DummyClock(now_value=datetime.datetime(2014, 1, 1, 0, 0, 0))
        self.fs = FakeFs()
        my_input = lambda: "y"
        randint = lambda: 44
        volumes = create_fake_volume_of(['/'])
        self.stderr = StringIO()
        self.cmd = make_cmd(clock=clock,
                            fs=self.fs,
                            my_input=my_input,
                            randint=randint,
                            stderr=self.stderr,
                            volumes=volumes)

    def test_when_file_does_not_exist(self):
        result = self.run_cmd(['trash-put', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result == [
            ["trash-put: cannot trash non existent 'non-existent'"],
            'None',
            EX_IOERR
        ]

    def test_when_file_does_not_exist_with_force(self):
        result = self.run_cmd(['trash-put', '-f', 'non-existent'],
                              {"HOME": "/home/user"}, 123)

        assert result == [[], 'None', 0]

    def test_put_does_not_tries_to_trash_file_in_trash_dir_when_non_exisiting(
            self):
        result = self.run_cmd(['trash-put', '-vvv', 'non-existing'],
                              {"HOME": "/home/user"}, 123)

        assert result == \
               [["trash-put: cannot trash non existent 'non-existing'"], 'None',
                EX_IOERR]

    def test_when_file_exists(self):
        self.fs.make_file("pippo")
        assert True == self.fs.exists("pippo")

        result = self.run_cmd(['trash-put', 'pippo'],
                              {"HOME": "/home/user"}, 123)

        assert False == self.fs.exists("pippo")
        assert EX_OK == result[2]
        assert ['pippo.trashinfo'] == self.fs.ls_aa(
            '/home/user/.local/share/Trash/info')
        assert ['pippo'] == self.fs.ls_aa(
            '/home/user/.local/share/Trash/files')

    def run_cmd(self, args, environ, uid):
        err = None
        exit_code = None
        try:
            exit_code = self.cmd.run(args, environ, uid)
        except IOError as e:
            err = e
        stderr = self.stderr.getvalue().splitlines()

        return [stderr, str(err), exit_code]
