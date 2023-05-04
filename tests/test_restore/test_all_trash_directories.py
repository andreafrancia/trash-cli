import unittest

from trashcli.fstab.volumes import FakeVolumes2
from trashcli.restore.trash_directories import TrashDirectories1


class TestTrashDirectories(unittest.TestCase):
    def setUp(self):
        environ = {'HOME': '~'}
        self.volumes = FakeVolumes2("volume_of(%s)", [])
        self.trash_directories = TrashDirectories1(self.volumes, 123, environ)

    def test_list_all_directories(self):
        self.volumes.set_volumes(['/', '/mnt'])

        result = list(self.trash_directories.all_trash_directories())

        assert ([
                    ('~/.local/share/Trash', 'volume_of(~/.local/share/Trash)'),
                    ('/.Trash/123', '/'),
                    ('/.Trash-123', '/'),
                    ('/mnt/.Trash/123', '/mnt'),
                    ('/mnt/.Trash-123', '/mnt')] ==
                result)
