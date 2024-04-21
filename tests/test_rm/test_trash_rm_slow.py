import unittest

import pytest
from six import StringIO

from tests.support.fake_trash_dir import FakeTrashDir
from tests.support.my_path import MyPath
from trashcli.fstab.volume_listing import NoVolumesListing
from trashcli.rm.main import RealRmFileSystemReader
from trashcli.rm.rm_cmd import RmCmd


@pytest.mark.slow
class TestTrashRm(unittest.TestCase):
    def setUp(self):
        self.xdg_data_home = MyPath.make_temp_dir()
        self.stderr = StringIO()
        self.trash_rm = RmCmd(environ={'XDG_DATA_HOME': self.xdg_data_home},
                              getuid=lambda: 123,
                              volumes_listing=NoVolumesListing(),
                              stderr=self.stderr,
                              file_reader=RealRmFileSystemReader())
        self.fake_trash_dir = FakeTrashDir(self.xdg_data_home / 'Trash')

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

    def tearDown(self):
        self.xdg_data_home.clean_up()
