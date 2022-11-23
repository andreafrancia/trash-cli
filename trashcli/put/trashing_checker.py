from trashcli.put.gate import Gate, ClosedGate, SameVolumeGate, HomeFallbackGate
from typing import Dict, TypeVar, Union, Type

from trashcli.put.candidate import Candidate
from trashcli.put.gate_impl import GateCheckResult, GateImpl, ClosedGateImpl, \
    SameVolumeGateImpl, HomeFallbackGateImpl
from trashcli.put.trashee import Trashee

Gate_ = Type[Union[ClosedGate, HomeFallbackGate, SameVolumeGate]]
GateImpl_ = Union[ClosedGateImpl, HomeFallbackGateImpl, SameVolumeGateImpl]

class TrashingChecker:
    def __init__(self, gates): # type: (Dict[Gate_, GateImpl_]) -> None
        self.gates = gates

    def file_could_be_trashed_in(self,
                                 trashee,  # type: Trashee
                                 candidate,  # type: Candidate,
                                 environ,  # type: Dict[str, str]
                                 ):  # type: (...) -> GateCheckResult
        gate = self.gates[candidate.gate]

        return gate.can_trash_in(trashee, candidate, environ)
