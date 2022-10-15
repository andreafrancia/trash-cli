import unittest

import pytest

from trashcli.fs import FileSystemReader
from trashcli.rm import ListTrashinfos
from .fake_trash_dir import FakeTrashDir
from .support.my_path import MyPath


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
