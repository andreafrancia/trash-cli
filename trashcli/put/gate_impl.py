from typing import NamedTuple, Optional

from trashcli.compat import Protocol
from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.fs.fs import Fs
from trashcli.put.trash_dir_volume_reader import TrashDirVolumeReader
from trashcli.put.trashee import Trashee
from trashcli.put.volume_message_formatter import VolumeMessageFormatter


class GateCheckResult(NamedTuple('GateCheckResult', [
    ('ok', bool),
    ('reason', Optional[str]),
])):

    @staticmethod
    def make_ok():
        return GateCheckResult(True, None)

    @staticmethod
    def make_error(reason):
        return GateCheckResult(False, reason)

    def __repr__(self):
        if self.ok and self.reason is None:
            return 'GateCheckResult.ok()'
        if not self.ok and self.reason is not None:
            return 'GateCheckResult.error(%r)' % self.reason
        return 'GateCheckResult(%s, %r)' % (self.ok, self.reason)


class GateImpl(Protocol):
    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Environ
                     ):  # type: (...) -> GateCheckResult
        raise NotImplementedError


class ClosedGateImpl(GateImpl):

    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Environ
                     ):  # type: (...) -> GateCheckResult
        return GateCheckResult.make_error("trash dir not enabled: %s" %
                                          candidate.shrink_user(environ))


class HomeFallbackGateImpl(GateImpl):
    def __init__(self,
                 fs,  # type: Fs
                 ):
        self.fs = fs

    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Environ
                     ):
        if environ.get('TRASH_ENABLE_HOME_FALLBACK', None) == "1":
            return GateCheckResult.make_ok()
        return GateCheckResult.make_error("trash dir not enabled: %s" %
                                          candidate.shrink_user(environ))


class SameVolumeGateImpl(GateImpl):
    def __init__(self,
                 trash_dir_volume,  # type: TrashDirVolumeReader
                 ):
        self.trash_dir_volume = trash_dir_volume

    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Environ
                     ):
        same_volume = self.trash_dir_volume.volume_of_trash_dir(
            candidate.trash_dir_path) == trashee.volume

        if not same_volume:
            msg_formatter = VolumeMessageFormatter()
            message = msg_formatter.format_msg(trashee, candidate, environ)
            return GateCheckResult.make_error(message)

        return GateCheckResult.make_ok()
