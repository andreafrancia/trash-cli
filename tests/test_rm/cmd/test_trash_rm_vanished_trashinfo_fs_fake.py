from six import StringIO

from tests.support.dates import date_at
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.another_process_removes_before_read import \
    AnotherProcessRemovesBeforeRead
from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.trash_dirs.given_trash import GivenTrash
from trashcli.rm.rm_cmd import RmCmd


class TestTrashRmVanishedTrashinfoFsFake:
    def setup_method(self):
        self.fs = FakeFs()
        self.trash = GivenTrash(self.fs)
        self.stderr = StringIO()
        self.rm_cmd = RmCmd(
            environ={'XDG_DATA_HOME': '/xdg'},
            getuid=lambda: 123,
            volumes_listing=FakeVolumesListing(),
            stderr=self.stderr,
            file_reader=AnotherProcessRemovesBeforeRead(
                self.fs, self.fs, '/xdg/Trash/info/bar.trashinfo'))

    def test_skips_the_trashinfo_removed_by_another_process(self):
        self.trash.has_trashed_file('/foo', '/xdg/Trash', date_at(2000, 1, 1))
        self.trash.has_trashed_file('/bar', '/xdg/Trash', date_at(2000, 1, 1))

        self.rm_cmd.run(['trash-rm', 'foo'], uid=123)

        assert self.fs.listdir('/xdg/Trash/info') == []
        assert self.fs.listdir('/xdg/Trash/files') == []
        assert self.stderr.getvalue() == ''
