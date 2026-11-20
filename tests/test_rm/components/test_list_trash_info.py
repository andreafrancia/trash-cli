import pytest

from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from trashcli.fslib.file_system_reader import FileSystemReader
from trashcli.rm.list_trashinfo import ListTrashinfos

fs = real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestListTrashinfos:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.tmp_dir = temp_dir
        self.trash_dir = temp_dir / 'Trash'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir, fs)
        self.listing = ListTrashinfos.make(FileSystemReader(fs), FileSystemReader(fs))

    def test_absolute_path(self):
        self.fake_trash_dir.add_trashinfo_basename_path('a', '/foo')

        result = list(self.listing.list_from_volume_trashdir(self.trash_dir,
                                                             '/volume/'))

        assert result == [('trashed_file',
                           ('/foo', '%s/info/a.trashinfo' % self.trash_dir))]

    def test_relative_path(self):
        self.fake_trash_dir.add_trashinfo_basename_path('a', 'foo')

        result = list(self.listing.list_from_volume_trashdir(self.trash_dir,
                                                             '/volume/'))

        assert result == [('trashed_file',
                           ('/volume/foo', '%s/info/a.trashinfo' % self.trash_dir))]

