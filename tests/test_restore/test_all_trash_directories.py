import unittest

from mock import Mock
from trashcli.restore.trash_directories import TrashDirectories


class TestTrashDirectories(unittest.TestCase):
    def setUp(self):
        volume_of = lambda x: "volume_of(%s)" % x
        environ = {'HOME': '~'}
        self.trash_directories = TrashDirectories(volume_of, 123, environ)

    def test_list_all_directories(self):
        result = list(self.trash_directories.all_trash_directories(
            ['/', '/mnt']
        ))

        assert ([
            ('~/.local/share/Trash', 'volume_of(~/.local/share/Trash)'),
            ('/.Trash/123', '/'),
            ('/.Trash-123', '/'),
            ('/mnt/.Trash/123', '/mnt'),
            ('/mnt/.Trash-123', '/mnt')] ==
            result)
