import unittest

from mock import Mock

from tests.support.fake_volumes import make_fake_volumes_from
from trashcli.put.trash_dir_volume_reader import TrashDirVolumeReader


class TestTrashDirVolume(unittest.TestCase):
    def setUp(self):
        volumes = make_fake_volumes_from(['/disk1', '/disk2'])
        fs = Mock()
        fs.realpath = lambda path: path
        self.trash_dir_volume = TrashDirVolumeReader(volumes, fs)

    def test(self):
        result = self.trash_dir_volume.volume_of_trash_dir('/disk1/trash_dir_path')
        assert result == '/disk1'
