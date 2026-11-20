import pytest
from six import StringIO

from tests.support.dates import date_at
from tests.support.dirs.temp_dir import make_temp_dir
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.another_process_removes_before_read import \
    AnotherProcessRemovesBeforeRead
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from trashcli.fslib.real.real_fs import RealFs
from trashcli.rm.main import RealRmFileSystemReader
from trashcli.rm.rm_cmd import RmCmd


@pytest.mark.slow
class TestTrashRmVanishedTrashinfoFsReal:
    def setup_method(self):
        self.fs = RealFs()
        self.tmp_dir = make_temp_dir(self.fs)
        self.xdg = str(self.tmp_dir / 'xdg')
        self.trash_dir = FakeTrashDir(self.tmp_dir / 'xdg' / 'Trash')
        self.stderr = StringIO()
        self.rm_cmd = RmCmd(
            environ={'XDG_DATA_HOME': self.xdg},
            getuid=lambda: 123,
            volumes_listing=FakeVolumesListing(),
            stderr=self.stderr,
            file_reader=AnotherProcessRemovesBeforeRead(
                RealRmFileSystemReader(self.fs), self.fs,
                self.xdg + '/Trash/info/bar.trashinfo'))

    def test_skips_the_trashinfo_removed_by_another_process(self):
        self.trash_dir.add_trashed_file('foo', '/foo', 'content',
                                        date_at(2000, 1, 1))
        self.trash_dir.add_trashed_file('bar', '/bar', 'content',
                                        date_at(2000, 1, 1))

        self.rm_cmd.run(['trash-rm', 'foo'], uid=123)

        assert self.fs.listdir(self.xdg + '/Trash/info') == []
        assert self.fs.listdir(self.xdg + '/Trash/files') == []
        assert self.stderr.getvalue() == ''

    def teardown_method(self):
        self.tmp_dir.clean_up()
