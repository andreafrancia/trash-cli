# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
from tests.support.fakes.fake_file_system import FakeFileSystem

from trashcli.lib.trash_dir_reader import TrashDirReader


class TestTrashDirReader:
    def setup_method(self):
        self.fs = FakeFileSystem()
        self.trash_dir = TrashDirReader(self.fs)

    def test(self):
        self.fs.create_fake_file('/info/foo.trashinfo')

        result = list(self.trash_dir.list_orphans('/'))

        assert [] == result

    def test2(self):
        self.fs.create_fake_file('/files/foo')

        result = list(self.trash_dir.list_orphans('/'))

        assert ['/files/foo'] == result
