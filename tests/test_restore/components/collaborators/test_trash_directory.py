import pytest

from tests.support.fs_fixture import real_fs_fixture, fsx_fixture
from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture
from trashcli.restore.info_files import InfoFiles

fs = real_fs_fixture
temp_dir = temp_dir_fixture
fsx = fsx_fixture

@pytest.mark.slow
class TestTrashDirectory:
    @pytest.fixture(autouse=True)
    def setup_method(self, fs, temp_dir, fsx):
        self.fsx = fsx
        self.temp_dir = make_temp_dir(fs)
        self.fsx.require_empty_dir(self.temp_dir / 'trash-dir')
        self.info_files = InfoFiles(fs)

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
