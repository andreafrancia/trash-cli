from typing import cast

from trashcli.fstab.volumes import FakeVolumes
from trashcli.put.candidate import Candidate
from trashcli.put.gate import SameVolumeGate, HomeFallbackGate
from trashcli.put.trashee import Trashee
from trashcli.put.trashing_checker import TrashDirChecker
from .support.fake_fs.fake_fs import FakeFs


class Value:
    def __init__(self, values):
        self.__dict__ = values


def mock_value(type, **kwargs):
    return cast(type, Value(kwargs))


class TestTrashingChecker:
    def setup_method(self):
        self.fs = FakeFs()
        self.volumes = FakeVolumes(["/"])
        self.checker = TrashDirChecker(self.fs, self.volumes)

    def test_trashing_checker_same(self):
        self.volumes.add_volume('/volume1')

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/volume1'),
            make_candidate('/volume1/trash-dir', SameVolumeGate),
            {})

        assert result.ok is True

    def test_home_in_same_volume(self):

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/volume1'),
            make_candidate('/home-vol/trash-dir', HomeFallbackGate),
            {})

        assert result.ok is False

    def test_trashing_checker_different(self):
        self.volumes.add_volume("/vol1")
        self.volumes.add_volume("/vol2")

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/vol1'),
            make_candidate('/vol2/trash-dir-path', SameVolumeGate),
            {})

        assert result.ok is False
        assert result.reason == "won't use trash dir /vol2/trash-dir-path because its volume (/vol2) in a different volume than /path1 (/vol1)"


def make_candidate(trash_dir_path, gate):
    return Candidate(trash_dir_path=trash_dir_path,
                     path_maker_type=None,
                     check_type=None,
                     gate=gate,
                     volume="ignored")
