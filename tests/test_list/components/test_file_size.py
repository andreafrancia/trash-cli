from tests.support.dirs.temp_dir import temp_dir  # noqa

from trashcli.fslib.real.real_file_size import RealFileSize
from tests.support.files import fsx

fsx = fsx  # the fixture, imported from its module


class TestFileSize:
    def test(self, temp_dir, fsx):
        fsx.make_file(temp_dir / 'a-file', '123')
        result = RealFileSize().file_size(temp_dir / 'a-file')
        assert 3 == result
