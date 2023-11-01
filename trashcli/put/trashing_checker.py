from typing import NamedTuple, List

from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.core.either import Either, Right, Left
from trashcli.put.core.failure_reason import FailureReason, LogContext, Level, \
    LogEntry
from trashcli.put.fs.fs import Fs
from trashcli.put.gate import Gate
from trashcli.put.trash_dir_volume_reader import TrashDirVolumeReader
from trashcli.put.trashee import Trashee


class TrashDirCannotBeUsed(NamedTuple('TrashDirCannotBeUsed', [
    ('reason', str),
]), FailureReason):
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        return [LogEntry(Level.INFO, self.reason)]


GateCheckResult = Either[None, TrashDirCannotBeUsed]


class TrashDirChecker:
    def __init__(self, fs, volumes):  # type: (Fs, VolumeOf) -> None
        self.fs = fs
        self.volumes = volumes

    def file_could_be_trashed_in(self,
                                 trashee,  # type: Trashee
                                 candidate,  # type: Candidate
                                 environ,  # type: Environ
                                 ):  # type: (...) -> GateCheckResult
        if candidate.gate is Gate.HomeFallback:
            return self._can_be_trashed_in_home_trash_dir(candidate, environ)
        elif candidate.gate is Gate.SameVolume:
            return SameVolumeGateImpl(self.volumes, self.fs).can_trash_in(
                trashee, candidate, environ)
        else:
            raise ValueError("Unknown gate: %s" % candidate.gate)

    @staticmethod
    def _can_be_trashed_in_home_trash_dir(candidate,  # type: Candidate
                                          environ,  # type: Environ
                                          ):
        if environ.get('TRASH_ENABLE_HOME_FALLBACK', None) == "1":
            return make_ok()
        return make_error("trash dir not enabled: %s" %
                          candidate.shrink_user(environ))


def make_ok():
    return Right(None)


def make_error(reason):
    return Left(TrashDirCannotBeUsed(reason))


class SameVolumeGateImpl:
    def __init__(self,
                 volumes,  # type: VolumeOf
                 fs,  # type: Fs
                 ):
        self.volumes = volumes
        self.fs = fs

    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Environ
                     ):
        trash_dir_volume = self._volume_of_trash_dir(candidate)
        same_volume = trash_dir_volume == trashee.volume

        if not same_volume:
            message = self._format_msg(trashee, candidate, environ,
                                       trash_dir_volume)
            return make_error(message)

        return make_ok()

    def _volume_of_trash_dir(self, candidate):  # type: (Candidate) -> str
        return (TrashDirVolumeReader(self.volumes, self.fs)
                .volume_of_trash_dir(candidate.trash_dir_path))

    @staticmethod
    def _format_msg(trashee,  # type: Trashee
                    candidate,  # type: Candidate
                    environ,  # type: Environ
                    volume_of_trash_dir,  # type: str
                    ):
        formatted_dir = candidate.shrink_user(environ)

        return (
                "won't use trash dir %s because its volume (%s) in a different volume than %s (%s)"
                % (formatted_dir, volume_of_trash_dir, trashee.path,
                   trashee.volume))
