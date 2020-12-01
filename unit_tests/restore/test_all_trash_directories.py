import unittest
from mock import Mock
from nose.tools import assert_equal
from trashcli.restore import AllTrashDirectories


class TestTrashDirectories(unittest.TestCase):
    def setUp(self):
        self.all_trash_directories = AllTrashDirectories(
                volume_of    = Mock(),
                getuid       = lambda:123,
                environ      = {'HOME': '~'},
                mount_points = ['/', '/mnt'])

    def test_list_all_directories(self):

        result = self.all_trash_directories.all_trash_directories()
        paths = list(map(lambda td: td.path, result))

        assert_equal(['~/.local/share/Trash',
                      '/.Trash/123',
                      '/.Trash-123',
                      '/mnt/.Trash/123',
                      '/mnt/.Trash-123'], paths)
