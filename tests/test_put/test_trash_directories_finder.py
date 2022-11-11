import unittest

from mock import Mock

from trashcli.put.candidate import Candidate
from trashcli.put.gate import SameVolumeGate, HomeFallbackGate
from trashcli.put.path_maker import AbsolutePaths, RelativePaths
from trashcli.put.security_check import NoCheck, TopTrashDirCheck
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

        assert result == [
            Candidate(trash_dir_path='~/.local/share/Trash',
                      volume='volume_of(~/.local/share/Trash)',
                      path_maker_type=AbsolutePaths,
                      check_type=NoCheck, gate=SameVolumeGate),
            Candidate(trash_dir_path='/volume/.Trash/123', volume='/volume',
                      path_maker_type=RelativePaths,
                      check_type=TopTrashDirCheck, gate=SameVolumeGate),
            Candidate(trash_dir_path='/volume/.Trash-123', volume='/volume',
                      path_maker_type=RelativePaths,
                      check_type=NoCheck, gate=SameVolumeGate),
            Candidate(trash_dir_path='~/.local/share/Trash',
                      volume='volume_of(~/.local/share/Trash)',
                      path_maker_type=AbsolutePaths,
                      check_type=NoCheck, gate=HomeFallbackGate),
        ]

    def test_specific_user_dir(self):
        result = self.finder.possible_trash_directories_for('/volume',
                                                            'user_dir',
                                                            self.environ,
                                                            123,
                                                            True)

        assert result == [('user_dir',
                           'volume_of(user_dir)',
                           RelativePaths,
                           NoCheck,
                           SameVolumeGate)]
