import pytest
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from trashcli.rm.main import RealRmFileSystemReader
from trashcli.rm.rm_cmd import RmCmd


fs =  real_fs_fixture
temp_dir = temp_dir_fixture

@pytest.mark.slow
class TestTrashRm:
    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.xdg_data_home = temp_dir
        self.stderr = StringIO()
        self.trash_rm = RmCmd(environ={'XDG_DATA_HOME': self.xdg_data_home},
                              getuid=lambda: 123,
                              volumes_listing=FakeVolumesListing(),
                              stderr=self.stderr,
                              file_reader=RealRmFileSystemReader(fs))
        self.fake_trash_dir = FakeTrashDir(self.xdg_data_home / 'Trash', fs)

    def test_issue69(self):
        self.fake_trash_dir.add_trashinfo_without_path('foo')

        self.trash_rm.run(['trash-rm', 'ignored'], uid=None)

        assert (self.stderr.getvalue() ==
                "trash-rm: %s/Trash/info/foo.trashinfo: unable to parse 'Path'"
                '\n' % self.xdg_data_home)

    def test_integration(self):
        self.fake_trash_dir.add_trashinfo_basename_path("del", 'to/be/deleted')
        self.fake_trash_dir.add_trashinfo_basename_path("keep", 'to/be/kept')

        self.trash_rm.run(['trash-rm', 'delete*'], uid=None)

        assert self.fake_trash_dir.ls_info() == ['keep.trashinfo']
