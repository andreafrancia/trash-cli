import unittest

from tests.support.py2mock import Mock

from trashcli.put.core.candidate import Candidate
from trashcli.put.core.check_type import NoCheck, TopTrashDirCheck
from trashcli.put.core.path_maker_type import PathMakerType
from trashcli.put.gate import Gate
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder


class TestTrashDirectoriesFinder(unittest.TestCase):
    def setUp(self):
        volumes = Mock(spec=[])
        volumes.volume_of = lambda x: 'volume_of(%s)' % x
        self.environ = {'HOME': "~"}
        self.finder = TrashDirectoriesFinder(volumes)

    def test_no_specific_user_dir(self):
        result = self.finder.possible_trash_directories_for('/volume', None,
                                                            self.environ, 123,
                                                            True)

        assert list(result) == [
            Candidate(trash_dir_path='~/.local/share/Trash',
                      volume='volume_of(~/.local/share/Trash)',
                      path_maker_type=PathMakerType.AbsolutePaths,
                      check_type=NoCheck, gate=Gate.SameVolume),
            Candidate(trash_dir_path='/volume/.Trash/123', volume='/volume',
                      path_maker_type=PathMakerType.RelativePaths,
                      check_type=TopTrashDirCheck, gate=Gate.SameVolume),
            Candidate(trash_dir_path='/volume/.Trash-123', volume='/volume',
                      path_maker_type=PathMakerType.RelativePaths,
                      check_type=NoCheck, gate=Gate.SameVolume),
            Candidate(trash_dir_path='~/.local/share/Trash',
                      volume='volume_of(~/.local/share/Trash)',
                      path_maker_type=PathMakerType.AbsolutePaths,
                      check_type=NoCheck, gate=Gate.HomeFallback),
        ]

    def test_specific_user_dir(self):
        result = self.finder.possible_trash_directories_for('/volume',
                                                            'user_dir',
                                                            self.environ,
                                                            123,
                                                            True)

        assert list(result) == [('user_dir',
                                 'volume_of(user_dir)',
                                 PathMakerType.RelativePaths,
                                 NoCheck,
                                 Gate.SameVolume)]
