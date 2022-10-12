import unittest

from mock import Mock

from trashcli.fstab import create_fake_volume_of
from trashcli.put.trash_dir_volume import TrashDirVolume


class TestTrashDirVolume(unittest.TestCase):
    def setUp(self):
        volumes = create_fake_volume_of(['/disk1', '/disk2'])
        fs = Mock()
        fs.realpath = lambda path: path
        self.trash_dir_volume = TrashDirVolume(volumes, fs)

    def test(self):
        result = self.trash_dir_volume.volume_of_trash_dir('/disk1/trash_dir_path')
        assert result == '/disk1'
