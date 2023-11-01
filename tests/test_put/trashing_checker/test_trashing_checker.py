from trashcli.fstab.volumes import FakeVolumes
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.either import Left
from trashcli.put.core.trashee import Trashee
from trashcli.put.gate import Gate
from trashcli.put.janitor_tools.trash_dir_checker import TrashDirChecker, \
    DifferentVolumes
from ..support.fake_fs.fake_fs import FakeFs


class TestTrashingChecker:
    def setup_method(self):
        self.fs = FakeFs()
        self.volumes = FakeVolumes(["/"])
        self.checker = TrashDirChecker(self.fs, self.volumes)

    def test_trashing_checker_same(self):
        self.volumes.add_volume('/volume1')

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/volume1'),
            make_candidate('/volume1/trash-dir', Gate.SameVolume),
            {})

        assert result.is_valid() is True

    def test_home_in_same_volume(self):

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/volume1'),
            make_candidate('/home-vol/trash-dir', Gate.HomeFallback),
            {})

        assert result.is_valid() is False

    def test_trashing_checker_different(self):
        self.volumes.add_volume("/vol1")
        self.volumes.add_volume("/vol2")

        result = self.checker.file_could_be_trashed_in(
            Trashee('/path1', '/vol1'),
            make_candidate('/vol2/trash-dir-path', Gate.SameVolume),
            {})

        assert result == Left(DifferentVolumes("/vol2", "/vol1"))

def make_candidate(trash_dir_path, gate):
    return Candidate(trash_dir_path=trash_dir_path,
                     path_maker_type=None,
                     check_type=None,
                     gate=gate,
                     volume="ignored")
