import unittest

import flexmock
from typing import cast

from trashcli.put.candidate import Candidate
from trashcli.put.gate import SameVolumeGate, ClosedGate, HomeFallbackGate
from trashcli.put.gate_impl import ClosedGateImpl, HomeFallbackGateImpl, \
    SameVolumeGateImpl
from trashcli.put.trash_dir_volume_reader import TrashDirVolumeReader
from trashcli.put.trashee import Trashee
from trashcli.put.trashing_checker import TrashingChecker


class Value:
    def __init__(self, values):
        self.__dict__ = values


def mock_value(type, **kwargs):
    return cast(type, Value(kwargs))


class TestTrashingChecker(unittest.TestCase):
    def setUp(self):
        self.trash_dir_volume = flexmock.Mock()
        self.checker = TrashingChecker(
            {
                ClosedGate: ClosedGateImpl(),
                HomeFallbackGate: HomeFallbackGateImpl(),
                SameVolumeGate: SameVolumeGateImpl(
                    cast(TrashDirVolumeReader, self.trash_dir_volume)),
            })

    def test_trashing_checker_same(self):
        self.trash_dir_volume.should_receive('volume_of_trash_dir') \
            .with_args('trash-dir-path').and_return('/volume1')

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/volume1'),
            make_candidate('trash-dir-path', SameVolumeGate, '/disk1'),
            {})

        assert result.ok is True

    def test_home_in_same_volume(self):
        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/volume1'),
            make_candidate('trash-dir-path', HomeFallbackGate, '/disk1'),
            {})

        assert result.ok is False

    def test_trashing_checker_different(self):
        self.trash_dir_volume.should_receive('volume_of_trash_dir') \
            .with_args('trash-dir-path').and_return('/volume2')

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/volume1'),
            make_candidate('trash-dir-path', SameVolumeGate, '/disk1'),
            {})

        assert result.ok is False
        assert result.reason == "won't use trash dir trash-dir-path because its volume (/disk1) in a different volume than /path1 (/volume1)"


def make_candidate(trash_dir_path, gate, volume):
    return Candidate(trash_dir_path=trash_dir_path,
                     path_maker_type=None,
                     check_type=None,
                     gate=gate,
                     volume=volume)
