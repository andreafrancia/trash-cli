import os

from trashcli.put.fs.real_fs import RealFs
from tests.support.dirs.temp_dir import temp_dir

temp_dir = temp_dir


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
