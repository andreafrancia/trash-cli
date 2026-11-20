import pytest

from tests.support.fakes.fake_file_system import FakeFileSystem
from tests.support.fakes.fake_file_system import UnreadableFileSystem
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.rm.list_trashinfo import ListTrashinfos


class TestListTrashinfosVanished:
    def setup_method(self):
        self.fs = FakeFileSystem()
        self.listing = ListTrashinfos(self.fs, TrashDirReader(self.fs))

    def test_skips_trashinfo_removed_after_the_listing(self):
        self.fs.create_fake_file('/trash/info/b.trashinfo',
                                 '[Trash Info]\nPath=/b\n')
        self.fs.create_fake_dir('/trash/info', 'a.trashinfo', 'b.trashinfo')

        result = list(self.listing.list_from_volume_trashdir('/trash', '/'))

        assert result == [('trashed_file', ('/b', '/trash/info/b.trashinfo'))]

    def test_other_read_errors_are_not_swallowed(self):
        fs = UnreadableFileSystem()
        fs.create_fake_dir('/trash/info', 'a.trashinfo')
        listing = ListTrashinfos(fs, TrashDirReader(fs))

        with pytest.raises(IOError):
            list(listing.list_from_volume_trashdir('/trash', '/'))
