import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture, fsx_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture


@pytest.mark.slow
class TestRealFsListDir:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.fs = fs
        self.tmp_dir = temp_dir

    def test(self):
        self.fs.write_file(self.tmp_dir / 'a', 'content')
        self.fs.write_file(self.tmp_dir / 'b', 'content')
        self.fs.write_file(self.tmp_dir / 'c', 'content')
        self.fs.makedirs(self.tmp_dir / 'd', 0o700)

        assert sorted(self.fs.listdir(self.tmp_dir)) == ['a', 'b', 'c', 'd']

