from typing import Dict

from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.gate import Gate
from trashcli.put.gate_impl import GateCheckResult, GateImpl
from trashcli.put.trashee import Trashee


class TrashingChecker:
    def __init__(self, gates):  # type: (Dict[Gate, GateImpl]) -> None
        self.gates = gates

    def file_could_be_trashed_in(self,
                                 trashee,  # type: Trashee
                                 candidate,  # type: Candidate
                                 environ,  # type: Environ
                                 ):  # type: (...) -> GateCheckResult
        gate = self.gates[candidate.gate]

        return gate.can_trash_in(trashee, candidate, environ)
