import unittest

from tests.support.fakes.fake_volume_of import FakeVolumeOf
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.put.trash_dir_volume_reader import TrashDirVolumeReader


class TestTrashDirVolume(unittest.TestCase):
    def setUp(self):
        fs = FakeFs()
        fs.add_volume('/disk1')
        fs.add_volume('/disk2')
        self.reader = TrashDirVolumeReader(fs)

    def test(self):
        result = self.reader.volume_of_trash_dir('/disk1/trash_dir_path')
        assert result == '/disk1'
