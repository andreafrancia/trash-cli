import os

from tests.run_command import temp_dir
from trashcli.put.fs.real_fs import RealFs

# tell the IDE to don't remove temp_dir import during optimization
temp_dir = temp_dir  # this a pytest fixture


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
