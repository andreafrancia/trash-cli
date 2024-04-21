from tests.support.files import make_file
from tests.support.run_command import temp_dir  # noqa

from trashcli import fs


class TestFileSize:
    def test(self, temp_dir):
        make_file(temp_dir / 'a-file', '123')
        result = fs.file_size(temp_dir / 'a-file')
        assert 3 == result
