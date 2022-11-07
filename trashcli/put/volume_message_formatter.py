import os

from trashcli.put.candidate import Candidate
from trashcli.put.dir_formatter import DirFormatter
from trashcli.put.trashee import Trashee


class VolumeMessageFormatter:
    def __init__(self,
                 dir_formatter,  # type: DirFormatter
                 ):
        self.dir_formatter = dir_formatter

    def format_msg(self,
                   file_to_be_trashed,  # type: Trashee
                   candidate,  # type: Candidate
                   ):
        formatted_dir = self.dir_formatter.shrink_user(
            os.path.normpath(candidate.trash_dir_path))

        return (
                "won't use trash dir %s because its volume (%s) in a different volume than %s (%s)"
                % (formatted_dir,
                   candidate.volume,
                   file_to_be_trashed.path,
                   file_to_be_trashed.volume))
