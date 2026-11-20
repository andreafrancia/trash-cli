import pytest

from tests.support.fs_fixture import fsx_fixture
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture


@pytest.mark.slow
class TestMove:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, fsx, temp_dir):
        self.fs = fs
        self.fsx = fsx
        self.tmp_dir = temp_dir

    def test_two_files(self):
        self.fsx.make_file(self.tmp_dir / 'a', "AAAA")
        self.fsx.make_file(self.tmp_dir / 'b', "BBBB")

        result = self.fs.read_file(self.tmp_dir / 'b')

        assert result == 'BBBB'

    def test_move(self):
        self.fsx.make_file(self.tmp_dir / 'a', "AAAA")
        self.fsx.make_file(self.tmp_dir / 'b', "BBBB")

        self.fs.move(self.tmp_dir / 'a', self.tmp_dir / 'b')

        result = self.fs.read_file(self.tmp_dir / 'b')
        assert result == 'AAAA'
