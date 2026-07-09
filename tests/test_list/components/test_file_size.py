from tests.support.dirs.temp_dir import temp_dir  # noqa
from tests.support.files import make_file

from trashcli.fslib.real_fs_operations import RealFileSize


class TestFileSize:
    def test(self, temp_dir):
        make_file(temp_dir / 'a-file', '123')
        result = RealFileSize().file_size(temp_dir / 'a-file')
        assert 3 == result
