from tests.support.dirs.temp_dir import temp_dir_fixture

from trashcli.fslib.real.real_file_size import RealFileSize
from tests.support.fs_fixture import fsx_fixture, real_fs_fixture

fsx = fsx_fixture
temp_dir = temp_dir_fixture
fs = real_fs_fixture

class TestFileSize:
    def test(self, fs, temp_dir, fsx):
        fsx.make_file(temp_dir / 'a-file', '123')
        result = fs.file_size(temp_dir / 'a-file')
        assert 3 == result
