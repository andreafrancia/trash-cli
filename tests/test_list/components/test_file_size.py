from tests.support.files import make_file
from tests.support.temp_dir import temp_dir

from trashcli import fs


class TestFileSize:
    def test(self, temp_dir):
        make_file(temp_dir / 'a-file', '123')
        result = fs.file_size(temp_dir / 'a-file')
        assert 3 == result
