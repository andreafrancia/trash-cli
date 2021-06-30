import unittest

import pytest

from six import StringIO

from .support import MyPath
from trashcli.rm import RmCmd, ListTrashinfos
from .fake_trash_dir import FakeTrashDir
from trashcli.fs import FileSystemReader


@pytest.mark.slow
class TestTrashRm(unittest.TestCase):
    def setUp(self):
        self.xdg_data_home = MyPath.make_temp_dir()
        self.stderr = StringIO()
        self.trash_rm = RmCmd(environ = {'XDG_DATA_HOME': self.xdg_data_home}
                         , getuid = lambda: 123
                         , list_volumes = lambda:[]
                         , stderr = self.stderr
                         , file_reader = FileSystemReader())
        self.fake_trash_dir = FakeTrashDir(self.xdg_data_home / 'Trash')

    def test_issue69(self):
        self.fake_trash_dir.add_trashinfo_without_path('foo')

        self.trash_rm.run(['trash-rm', 'ignored'])

        assert (self.stderr.getvalue() ==
                "trash-rm: %s/Trash/info/foo.trashinfo: unable to parse 'Path'"
                '\n' % self.xdg_data_home)

    def test_integration(self):
        self.fake_trash_dir.add_trashinfo_basename_path("del", 'to/be/deleted')
        self.fake_trash_dir.add_trashinfo_basename_path("keep", 'to/be/kept')

        self.trash_rm.run(['trash-rm', 'delete*'])

        assert self.fake_trash_dir.ls_info() == ['keep.trashinfo']

    def tearDown(self):
        self.xdg_data_home.clean_up()


@pytest.mark.slow
class TestListTrashinfos(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.trash_dir = self.tmp_dir / 'Trash'
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)
        self.listing = ListTrashinfos(FileSystemReader())

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

    def tearDown(self):
        self.tmp_dir.clean_up()
