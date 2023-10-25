from trashcli.compat import Protocol
from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.core.gate_check_result import GateCheckResult
from trashcli.put.fs.fs import Fs
from trashcli.put.trash_dir_volume_reader import TrashDirVolumeReader
from trashcli.put.trashee import Trashee
from trashcli.put.volume_message_formatter import VolumeMessageFormatter


class GateImpl(Protocol):
    def can_trash_in(self,
                     trashee,  # type: Trashee
                     candidate,  # type: Candidate
                     environ,  # type: Environ
                     ):  # type: (...) -> GateCheckResult
        raise NotImplementedError


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
            return GateCheckResult.make_error(message)

        return GateCheckResult.make_ok()

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
