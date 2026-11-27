import pytest

from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import FsFixture, real_fs_fixture
from tests.support.tools.version_saver import VersionSaver

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestSaveNewVersion:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.fs = fs
        self.fsx = FsFixture(fs)
        self.tmp_dir = temp_dir
        self.saver = VersionSaver(fs)

    def test(self):
        self.fsx.make_file(self.tmp_dir / 'trash.py', """\
somecode before
version="0.20.1.20"
somecode after
dont change this line: version="0.20.1.20"
""")

        self.saver.save_new_version('0.21.5.11', self.tmp_dir / 'trash.py')

        result = self.fs.read_file(self.tmp_dir / "trash.py")
        assert result == """\
somecode before
version = '0.21.5.11'
somecode after
dont change this line: version="0.20.1.20"
"""

    def test2(self):
        self.fsx.make_file(self.tmp_dir / 'trash.py', """\
somecode before
    version="0.20.1.20"
somecode after
""")

        self.saver.save_new_version('0.21.5.11', self.tmp_dir / 'trash.py')

        result = self.fs.read_file(self.tmp_dir / "trash.py")
        assert result == """\
somecode before
    version="0.20.1.20"
somecode after
"""
