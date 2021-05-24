import unittest
from mock import Mock

from trashcli.put import TrashDirectoriesFinder


class TestTrashDirectoriesFinder(unittest.TestCase):
    def setUp(self):
        volumes = Mock(spec=[])
        volumes.volume_of = lambda x: 'volume_of(%s)' % x
        self.finder = TrashDirectoriesFinder({'HOME': "~"},
                                             lambda: 123, volumes)

    def test_no_specific_user_dir(self):
        result = self.finder.possible_trash_directories_for('/volume', None)

        assert result == [('~/.local/share/Trash',
                           'volume_of(~/.local/share/Trash)',
                           'absolute_paths',
                           'all_is_ok_rules'),
                          ('/volume/.Trash/123',
                           '/volume',
                           'relative_paths',
                           'top_trash_dir_rules'),
                          ('/volume/.Trash-123',
                           '/volume',
                           'relative_paths',
                           'all_is_ok_rules')]

    def test_specific_user_dir(self):
        result = self.finder.possible_trash_directories_for('/volume', 'user_dir')

        assert result == [('user_dir',
                           'volume_of(user_dir)',
                           'relative_paths',
                           'all_is_ok_rules')]
