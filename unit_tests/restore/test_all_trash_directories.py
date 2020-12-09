import unittest

from mock import Mock
from nose.tools import assert_equal
from trashcli.restore import TrashDirectories


class TestTrashDirectories(unittest.TestCase):
    def setUp(self):
        volume_of = lambda x: "volume_of(%s)" % x
        getuid = Mock(return_value=123)
        environ = {'HOME': '~'}
        self.trash_directories = TrashDirectories(volume_of, getuid, environ)

    def test_list_all_directories(self):
        result = list(self.trash_directories.all_trash_directories(
            ['/', '/mnt']
        ))

        assert_equal([
            ('~/.local/share/Trash', 'volume_of(~/.local/share/Trash)'),
            ('/.Trash/123', '/'),
            ('/.Trash-123', '/'),
            ('/mnt/.Trash/123', '/mnt'),
            ('/mnt/.Trash-123', '/mnt')],
            result)
