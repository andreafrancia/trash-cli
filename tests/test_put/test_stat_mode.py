import os

from tests.support.run_command import temp_dir  # noqa
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.octal import octal

class TestStatMode:
    def setup_method(self):
        self.fs = RealFs()
        self.old_umask = os.umask(0o777 - 0o755)

    def teardown_method(self):
        os.umask(self.old_umask)

    def test_mode_for_a_dir(self, temp_dir):
        self.fs.mkdir_with_mode(temp_dir / 'foo', 0o755)
        stat = self.fs.lstat(temp_dir / 'foo')
        assert octal(stat.mode) == '0o40755'

    def test_mode_for_a_file(self, temp_dir):
        self.fs.touch(temp_dir / 'foo')
        stat = self.fs.lstat(temp_dir / 'foo')
        assert octal(stat.mode) == '0o100644'

    def test_mode_for_a_symlink(self, temp_dir):
        os.umask(0o777 - 0o777)
        self.fs.symlink(temp_dir / 'foo', temp_dir / 'bar')
        stat = self.fs.lstat(temp_dir / 'bar')
        assert octal(stat.mode) == '0o120777'
