import pytest
from six import StringIO

from tests.support.dates import date_at
from tests.support.dirs.temp_dir import make_temp_dir
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.another_process_removes_before_read import \
    AnotherProcessRemovesBeforeRead
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class TestEmptyCmdVanishedTrashinfoFsReal:
    def setup_method(self):
        self.fs = RealFs()
        self.tmp_dir = make_temp_dir(self.fs)
        self.xdg = str(self.tmp_dir / 'xdg')
        self.trash_dir = FakeTrashDir(self.tmp_dir / 'xdg' / 'Trash')
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
                self.fs, self.fs, self.xdg + '/Trash/info/bar.trashinfo'),
            dir_reader=FileSystemDirReader(self.fs),
            version='unused',
            volumes=self.fs)

    def test_skips_the_trashinfo_removed_by_another_process(self):
        self.trash_dir.add_trashed_file('foo', '/foo', 'content',
                                        date_at(2000, 1, 1))
        self.trash_dir.add_trashed_file('bar', '/bar', 'content',
                                        date_at(2000, 1, 10))

        self.empty_cmd.run_cmd(['-f', '1'], {'XDG_DATA_HOME': self.xdg},
                               uid=123)

        assert self.fs.listdir(self.xdg + '/Trash/info') == []
        assert self.fs.listdir(self.xdg + '/Trash/files') == []
        assert self.err.getvalue() == ''

    def teardown_method(self):
        self.tmp_dir.clean_up()
