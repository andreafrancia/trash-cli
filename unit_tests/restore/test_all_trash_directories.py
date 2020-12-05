import unittest
from nose.tools import assert_equal
from trashcli.restore import AllTrashDirectories


class TestTrashDirectories(unittest.TestCase):
    def setUp(self):
        self.all_trash_directories = AllTrashDirectories(
                volume_of    = lambda x: "volume_of(%s)" % x,
                getuid       = lambda:123,
                environ      = {'HOME': '~'},
                mount_points = ['/', '/mnt'])

    def test_list_all_directories(self):

        result = list(self.all_trash_directories.all_trash_directories())

        assert_equal([
            ('~/.local/share/Trash', 'volume_of(~/.local/share/Trash)'),
            ('/.Trash/123', '/'),
            ('/.Trash-123', '/'),
            ('/mnt/.Trash/123', '/mnt'),
            ('/mnt/.Trash-123', '/mnt')],
            result)
