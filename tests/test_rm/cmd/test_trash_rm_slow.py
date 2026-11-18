import os
import unittest

import pytest
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.temp_dir import make_temp_dir
from trashcli.fslib.real.real_fs import RealFs
from trashcli.rm.main import RealRmFileSystemReader
from trashcli.rm.rm_cmd import RmCmd


@pytest.mark.slow
class TestTrashRm(unittest.TestCase):
    def setUp(self):
        fs = RealFs()
        self.xdg_data_home = make_temp_dir(fs)
        self.stderr = StringIO()
        self.remover_fs = RealFs()
        self.trash_rm = RmCmd(environ={'XDG_DATA_HOME': self.xdg_data_home},
                              getuid=lambda: 123,
                              volumes_listing=FakeVolumesListing(),
                              stderr=self.stderr,
                              file_reader=RealRmFileSystemReader(self.remover_fs))
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

    def test_it_keeps_a_dir_renamed_to_the_trash_dir_name_after_the_listing(self):
        self.fake_trash_dir.add_trashinfo_basename_path("del", 'to/be/deleted')
        os.makedirs(self.xdg_data_home / 'Trash/files')
        os.makedirs(self.xdg_data_home / 'project/files')
        open(self.xdg_data_home / 'project/files/del', 'w').close()
        lexists = self.remover_fs.path_lexists

        def swap_then_check(path):
            if os.path.exists(self.xdg_data_home / 'project'):
                os.rename(self.xdg_data_home / 'Trash', self.xdg_data_home / 'away')
                os.rename(self.xdg_data_home / 'project', self.xdg_data_home / 'Trash')
            return lexists(path)

        self.remover_fs.path_lexists = swap_then_check

        with pytest.raises(OSError):
            self.trash_rm.run(['trash-rm', 'delete*'], uid=None)

        assert os.path.exists(self.xdg_data_home / 'Trash/files/del')

    def tearDown(self):
        self.xdg_data_home.clean_up()
