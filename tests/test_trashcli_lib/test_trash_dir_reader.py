# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest

from tests.support.files import FsFixture
from tests.support.put.fake_fs.fake_fs import FakeFs

from trashcli.lib.trash_dir_reader import TrashDirReader


class TestTrashDirReader(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.trash_dir = TrashDirReader(self.fs)

    def test(self):
        FsFixture(self.fs).make_empty_file('/info/foo.trashinfo')

        result = list(self.trash_dir.list_orphans('/'))

        assert [] == result

    def test2(self):
        FsFixture(self.fs).make_empty_file('/files/foo')

        result = list(self.trash_dir.list_orphans('/'))

        assert ['/files/foo'] == result
