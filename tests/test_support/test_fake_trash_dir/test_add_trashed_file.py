import pytest

from tests.support.dates import jan_11_2001
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture, support_fs_fixture
from tests.support.fakes.fake_trash_dir import FakeTrashDir

fs = real_fs_fixture
temp_dir = temp_dir_fixture
support_fs = support_fs_fixture


class TestAddTrashedFileOfFakeTrashDir:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, support_fs, temp_dir):
        self.root = temp_dir
        self.support_fs = support_fs
        self.trash_dir = FakeTrashDir(self.root / "Trash", fs)
        self.cwd = self.root / "cwd"
        self.result = self.trash_dir.add_trashed_file('foo-bar',
                                                      self.cwd / 'foo-bar',
                                                      'content of foo-bar',
                                                      jan_11_2001())

    def test_it_creates_both_info_and_original_copy(self):
        assert sorted(self.support_fs.find_files_rel()) == [
            '/Trash/files/foo-bar',
            '/Trash/info/foo-bar.trashinfo']

    def test_it_creates_the_right_content_of_info(self):
        assert (self.support_fs.read('Trash/info/foo-bar.trashinfo') ==
                '[Trash Info]\n'
                'Path=' + self.cwd / 'foo-bar' + '\n' +
                'DeletionDate=2001-01-01T00:00:00\n')

    def test_it_creates_the_original_copy(self):
        assert self.support_fs.read(
            'Trash/files/foo-bar') == "content of foo-bar"

    def test_result(self):
        assert self.result.original_file == self.trash_dir / 'files' / 'foo-bar'
        assert self.result.info_file == self.trash_dir / 'info' / 'foo-bar.trashinfo'
        assert self.result.original_location == self.cwd / 'foo-bar'
        assert self.result.deletion_date == jan_11_2001()
