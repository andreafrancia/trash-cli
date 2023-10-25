from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.core.gate_check_result import GateCheckResult
from trashcli.put.fs.fs import Fs
from trashcli.put.gate import HomeFallbackGate, SameVolumeGate
from trashcli.put.gate_impl import HomeFallbackGateImpl, SameVolumeGateImpl
from trashcli.put.trashee import Trashee


class TrashDirChecker:
    def __init__(self, fs, volumes):  # type: (Fs, VolumeOf) -> None
        self.gates = {
            HomeFallbackGate: HomeFallbackGateImpl(fs),
            SameVolumeGate: SameVolumeGateImpl(volumes, fs)
        }

    def file_could_be_trashed_in(self,
                                 trashee,  # type: Trashee
                                 candidate,  # type: Candidate
                                 environ,  # type: Environ
                                 ):  # type: (...) -> GateCheckResult
        gate = self.gates[candidate.gate]

        return gate.can_trash_in(trashee, candidate, environ)
