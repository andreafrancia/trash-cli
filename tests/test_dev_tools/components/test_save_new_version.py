from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from tests.support.tools.version_saver import VersionSaver
from trashcli.put.fs.real_fs import RealFs


class TestSaveNewVersion:
    def setup_method(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()
        self.saver = VersionSaver(self.fs)
        self.fx = FsFixture(self.fs)

    def test(self):
        self.fx.make_text_file_p(self.tmp_dir / 'trash.py', """\
somecode before
version="0.20.1.20"
somecode after
dont change this line: version="0.20.1.20"
""")

        self.saver.save_new_version('0.21.5.11', self.tmp_dir / 'trash.py')

        result = self.fs.read_text_file(self.tmp_dir / "trash.py")
        assert result == """\
somecode before
version = '0.21.5.11'
somecode after
dont change this line: version="0.20.1.20"
"""

    def test2(self):
        self.fx.make_text_file_p(self.tmp_dir / 'trash.py', """\
somecode before
    version="0.20.1.20"
somecode after
""")

        self.saver.save_new_version('0.21.5.11', self.tmp_dir / 'trash.py')

        result = self.fs.read_text_file(self.tmp_dir / "trash.py")
        assert result == """\
somecode before
    version="0.20.1.20"
somecode after
"""

    def teardown_method(self):
        self.tmp_dir.clean_up()
