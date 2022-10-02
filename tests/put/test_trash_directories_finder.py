import unittest

from mock import Mock
from trashcli.put.path_maker import PathMakerType
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder


class TestTrashDirectoriesFinder(unittest.TestCase):
    def setUp(self):
        volumes = Mock(spec=[])
        volumes.volume_of = lambda x: 'volume_of(%s)' % x
        self.environ = {'HOME': "~"}
        self.finder = TrashDirectoriesFinder(volumes)

    def test_no_specific_user_dir(self):
        result = self.finder.possible_trash_directories_for('/volume', None,
                                                            self.environ, 123)

        assert result == [('~/.local/share/Trash',
                           'volume_of(~/.local/share/Trash)',
                           PathMakerType.absolute_paths,
                           'all_is_ok_rules'),
                          ('/volume/.Trash/123',
                           '/volume',
                           PathMakerType.relative_paths,
                           'top_trash_dir_rules'),
                          ('/volume/.Trash-123',
                           '/volume',
                           PathMakerType.relative_paths,
                           'all_is_ok_rules')]

    def test_specific_user_dir(self):
        result = self.finder.possible_trash_directories_for('/volume',
                                                            'user_dir',
                                                            self.environ,
                                                            123)

        assert result == [('user_dir',
                           'volume_of(user_dir)',
                           PathMakerType.relative_paths,
                           'all_is_ok_rules')]
