from tests.run_command import temp_dir
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.octal import octal


class TestStat:
    def setup_method(self):
        self.fs = RealFs()

    def test_mode_for_a_dir(self, temp_dir):
        self.fs.mkdir(temp_dir / 'foo')
        stat = self.fs.lstat(temp_dir / 'foo')
        assert octal(stat.mode) == '0o40755'

    def test_mode_for_a_file(self, temp_dir):
        self.fs.touch(temp_dir / 'foo')
        stat = self.fs.lstat(temp_dir / 'foo')
        assert octal(stat.mode) == '0o100644'

    def test_mode_for_a_symlink(self, temp_dir):
        self.fs.symlink(temp_dir / 'foo', temp_dir / 'bar')
        stat = self.fs.lstat(temp_dir / 'bar')
        assert octal(stat.mode) == '0o120755'
