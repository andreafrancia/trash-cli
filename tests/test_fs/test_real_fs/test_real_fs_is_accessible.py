import os

import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture, fsx_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture

@pytest.mark.slow
class TestRealFsIsAccessible:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.fs = fs
        self.tmp_dir = temp_dir

    def test_dangling_link(self):
        os.symlink('non-existent', self.tmp_dir / 'link')

        result = self.fs.is_accessible(self.tmp_dir / 'link')

        assert result is False

    def test_connected_link(self):
        self.fs.write_file(self.tmp_dir / 'link-target', '')
        os.symlink('link-target', self.tmp_dir / 'link')

        result = self.fs.is_accessible(self.tmp_dir / 'link')

        assert result is True

    def test_dangling_link_with_lexists(self):
        os.symlink('non-existent', self.tmp_dir / 'link')

        result = self.fs.path_lexists(self.tmp_dir / 'link')

        assert result is True

    def test_connected_link_with_lexists(self):
        self.fs.write_file(self.tmp_dir / 'link-target', '')
        os.symlink('link-target', self.tmp_dir / 'link')

        result = self.fs.path_lexists(self.tmp_dir / 'link')

        assert result is True
