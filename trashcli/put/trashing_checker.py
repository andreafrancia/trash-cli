from trashcli.put.gate import ClosedGate, SameVolumeGate, HomeFallbackGate
from trashcli.put.gate_impl import ClosedGateImpl, SameVolumeGateImpl, \
    HomeFallbackGateImpl
from typing import Dict

from trashcli.put.candidate import Candidate
from trashcli.put.gate_impl import GateCheckResult
from trashcli.put.trashee import Trashee


class TrashingChecker:
    def __init__(self, trash_dir_volume):
        self.trash_dir_volume = trash_dir_volume

    def file_could_be_trashed_in(self,
                                 trashee,  # type: Trashee
                                 candidate,  # type: Candidate,
                                 environ,  # type: Dict[str, str]
                                 ):  # type: (...) -> GateCheckResult
        gates = {
            ClosedGate: ClosedGateImpl(),
            HomeFallbackGate: HomeFallbackGateImpl(),
            SameVolumeGate: SameVolumeGateImpl(self.trash_dir_volume),
        }
        gate = gates[candidate.gate]

        return gate.can_trash_in(trashee, candidate, environ)
