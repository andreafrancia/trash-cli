from tests.support.dates import jan_11_2001
from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import FakeTrashDir


class TestAddTrashedFileOfFakeTrashDir:
    def setup_method(self):
        self.root = MyPath.make_temp_dir()
        self.trash_dir = FakeTrashDir(self.root / "Trash")
        self.cwd = self.root / "cwd"
        self.result = self.trash_dir.add_trashed_file('foo-bar',
                                                self.cwd / 'foo-bar',
                                                'content of foo-bar',
                                                jan_11_2001())

    def test_it_creates_both_info_and_original_copy(self):
        assert sorted(self.root.find_files_rel()) == [
            '/Trash/files/foo-bar',
            '/Trash/info/foo-bar.trashinfo']

    def test_it_creates_the_right_content_of_info(self):
        assert (self.root.read('Trash/info/foo-bar.trashinfo') ==
                '[Trash Info]\n'
                'Path=' + self.cwd / 'foo-bar' + '\n' +
                'DeletionDate=2001-01-01T00:00:00\n')

    def test_it_creates_the_original_copy(self):
        assert self.root.read('Trash/files/foo-bar') == "content of foo-bar"

    def test_result(self):
        assert self.result.original_file == self.trash_dir / 'files' / 'foo-bar'
        assert self.result.info_file == self.trash_dir / 'info' / 'foo-bar.trashinfo'
        assert self.result.original_location == self.cwd / 'foo-bar'
        assert self.result.deletion_date == jan_11_2001()
