from trashcli.lib.environ import Environ
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.trashee import Trashee


class VolumeMessageFormatter:
    def format_msg(self,
                   trashee,  # type: Trashee
                   candidate,  # type: Candidate
                   environ, # type: Environ
                   volume_of_trash_dir,  # type: str
                   ):
        formatted_dir = candidate.shrink_user(environ)

        return (
                "won't use trash dir %s because its volume (%s) in a different volume than %s (%s)"
                % (formatted_dir, volume_of_trash_dir, trashee.path,
                   trashee.volume))
