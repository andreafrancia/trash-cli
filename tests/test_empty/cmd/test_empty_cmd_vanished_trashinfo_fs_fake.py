from six import StringIO

from tests.support.dates import date_at
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.another_process_removes_before_read import \
    AnotherProcessRemovesBeforeRead
from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.trash_dirs.given_trash import GivenTrash
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader


class TestEmptyCmdVanishedTrashinfoFsFake:
    def setup_method(self):
        self.fs = FakeFs()
        self.trash = GivenTrash(self.fs)
        self.err = StringIO()
        self.empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=self.err,
            volumes_listing=FakeVolumesListing(),
            now=lambda: date_at(2000, 1, 10),
            file_reader=self.fs,
            file_remover=ExistingFileRemover(self.fs),
            content_reader=AnotherProcessRemovesBeforeRead(
                self.fs, self.fs, '/xdg/Trash/info/bar.trashinfo'),
            dir_reader=FileSystemDirReader(self.fs),
            version='unused',
            volumes=self.fs)

    def test_skips_the_trashinfo_removed_by_another_process(self):
        self.trash.has_trashed_file('/foo', '/xdg/Trash', date_at(2000, 1, 1))
        self.trash.has_trashed_file('/bar', '/xdg/Trash',
                                    date_at(2000, 1, 10))

        self.empty_cmd.run_cmd(['-f', '1'], {'XDG_DATA_HOME': '/xdg'},
                               uid=123)

        assert self.fs.listdir('/xdg/Trash/info') == []
        assert self.fs.listdir('/xdg/Trash/files') == []
        assert self.err.getvalue() == ''
