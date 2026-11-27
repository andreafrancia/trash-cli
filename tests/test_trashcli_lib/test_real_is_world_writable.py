import pytest

from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture


class TestRealIsWorldWritable:
    # focused integration test: exercises only is_world_writable on the real fs
    @pytest.fixture(autouse=True)
    def setup_sut(self, fs, temp_dir):
        self.tmp_dir = temp_dir
        self.checker = fs

    def test_a_private_dir_is_not_world_writable(
            self, fs):
        fs.chmod(self.tmp_dir, 0o700)

        result = self.checker.is_world_writable(self.tmp_dir)

        assert result is False

    def test_a_world_writable_dir_is_detected(self, fs):
        fs.chmod(self.tmp_dir, 0o777)

        result = self.checker.is_world_writable(self.tmp_dir)

        assert result is True

    def test_a_missing_path_is_not_world_writable(self, temp_dir):
        assert self.checker.is_world_writable(temp_dir / 'nope') is False

    def test_a_symlink_to_a_private_dir_is_not_world_writable(
            self, fs, temp_dir):
        fs.mkdir(temp_dir / 'dir', 0o700)
        fs.symlink(temp_dir / 'dir', temp_dir / 'link')

        result = self.checker.is_world_writable(temp_dir / 'link')

        assert result is False

    def test_a_symlink_to_a_world_writable_dir_is_detected(self, fs, temp_dir):
        fs.mkdir(temp_dir / 'dir')
        fs.chmod(temp_dir / 'dir', 0o777)
        fs.symlink(temp_dir / 'dir', temp_dir / 'link')

        result = self.checker.is_world_writable(temp_dir / 'link')

        assert result is True

    def test_a_dangling_symlink_is_not_world_writable(self, fs, temp_dir):
        fs.symlink(temp_dir / 'none', temp_dir / 'link')

        assert self.checker.is_world_writable(temp_dir / 'link') is False
