from tests.support.dirs.temp_dir import temp_dir  # noqa
from tests.support.fs_fixture import FsFixture

from trashcli.put.fs.real_fs import RealFs


class TestFileSize:
    def setup_method(self):
        self.fs = RealFs()
        self.fx = FsFixture(self.fs)
    def test(self, temp_dir):
        self.fx.make_file(temp_dir / 'a-file', b'123')
        result = self.fs.file_size(temp_dir / 'a-file')
        assert 3 == result
