from trashcli.lib.environ import Environ
from trashcli.put.candidate import Candidate
from trashcli.put.trashee import Trashee


class VolumeMessageFormatter:
    def format_msg(self,
                   trashee,  # type: Trashee
                   candidate,  # type: Candidate
                   environ, # type: Environ
                   ):
        formatted_dir = candidate.shrink_user(environ)

        return (
                "won't use trash dir %s because its volume (%s) in a different volume than %s (%s)"
                % (formatted_dir, candidate.volume, trashee.path,
                   trashee.volume))
