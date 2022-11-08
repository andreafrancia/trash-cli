from typing import Dict

from trashcli.put.candidate import Candidate
from trashcli.put.trash_dir_volume_reader import TrashDirVolumeReader
from trashcli.put.trashee import Trashee
from trashcli.put.volume_message_formatter import VolumeMessageFormatter


class GateCheckResult:
    def __init__(self, ok, reason):
        self.ok = ok
        self.reason = reason

    @staticmethod
    def ok():
        return GateCheckResult(True, None)

    @staticmethod
    def error(reason):
        return GateCheckResult(False, reason)


class GateImpl(object):
    @staticmethod
    def can_trash_in(trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Dict[str, str]
                     ):  # type (...) -> GateCheckResult
        pass


class ClosedGateImpl(GateImpl):

    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Dict[str, str]
                     ):
        return GateCheckResult.error("trash dir not enabled: %s" %
                                     candidate.shrink_user(environ))


class SameVolumeGateImpl(GateImpl):
    def __init__(self,
                 trash_dir_volume,  # type: TrashDirVolumeReader
                 ):
        self.trash_dir_volume = trash_dir_volume

    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Dict[str, str]
                     ):
        same_volume = self.trash_dir_volume.volume_of_trash_dir(
            candidate.trash_dir_path) == trashee.volume

        if not same_volume:
            msg_formatter = VolumeMessageFormatter()
            message = msg_formatter.format_msg(trashee, candidate, environ)
            return GateCheckResult.error(message)

        return GateCheckResult.ok()
