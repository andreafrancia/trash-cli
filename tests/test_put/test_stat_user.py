import getpass
import grp
import os

from tests.run_command import temp_dir
from trashcli.put.fs.real_fs import Names
from trashcli.put.fs.real_fs import RealFs


class TestNames:
    def setup_method(self):
        self.names = Names()

    def test_username(self):
        assert self.names.username(os.getuid()) == getpass.getuser()

    def test_group(self):
        assert self.names.groupname(os.getgid()) == _current_group()


class TestStatMode:
    def setup_method(self):
        self.fs = RealFs()

    def test_user(self, temp_dir):
        self.fs.touch(temp_dir / 'foo')
        stat = self.fs.lstat(temp_dir / 'foo')
        assert stat.uid == os.getuid()

    def test_group(self, temp_dir):
        self.fs.touch(temp_dir / 'foo')
        stat = self.fs.lstat(temp_dir / 'foo')
        assert stat.gid == os.getgid()


def _current_group():
    return grp.getgrgid(os.getgid()).gr_name
