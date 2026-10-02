import pytest

from tests.support.files import FsFixture
from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real.real_list_files_in_dir import RealListFilesInDir
from trashcli.restore.info_files import InfoFiles


@pytest.mark.slow
class TestTrashDirectory:
    def setup_method(self):
        self.fsx = FsFixture()
        self.temp_dir = MyPath.make_temp_dir()
        self.fsx.require_empty_dir(self.temp_dir / 'trash-dir')
        self.info_files = InfoFiles(RealListFilesInDir())

    def test_should_list_a_trashinfo(self):
        self.fsx.make_file(self.temp_dir / 'trash-dir/info/foo.trashinfo')

        result = self.list_trashinfos()

        assert [('trashinfo', self.temp_dir / 'trash-dir/info/foo.trashinfo')] == result

    def test_should_list_multiple_trashinfo(self):
        self.fsx.make_file(self.temp_dir / 'trash-dir/info/foo.trashinfo')
        self.fsx.make_file(self.temp_dir / 'trash-dir/info/bar.trashinfo')
        self.fsx.make_file(self.temp_dir / 'trash-dir/info/baz.trashinfo')

        result = self.list_trashinfos()

        assert sorted(result) == sorted([
            ('trashinfo', self.temp_dir / 'trash-dir/info/foo.trashinfo'),
            ('trashinfo', self.temp_dir / 'trash-dir/info/baz.trashinfo'),
            ('trashinfo', self.temp_dir / 'trash-dir/info/bar.trashinfo')])

    def test_non_trashinfo_should_reported_as_a_warn(self):
        self.fsx.make_file(self.temp_dir / 'trash-dir/info/not-a-trashinfo')

        result = self.list_trashinfos()

        assert sorted(result) == [
            ('non_trashinfo', self.temp_dir / 'trash-dir/info/not-a-trashinfo')]

    def list_trashinfos(self):
        return list(self.info_files.all_info_files(self.temp_dir / 'trash-dir'))

    def teardown_method(self):
        self.temp_dir.clean_up()
