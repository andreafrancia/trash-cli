import os
from datetime import datetime
from io import TextIOWrapper

from trashcli.empty.actions import Action
from trashcli.empty.console import Console
from trashcli.empty.delete_according_date import ContentReader
from trashcli.empty.empty_action import EmptyAction
from trashcli.empty.errors import Errors
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.is_input_interactive import is_input_interactive
from trashcli.empty.parser import Parser
from trashcli.empty.print_time_action import PrintTimeAction
from trashcli.empty.print_version_action import PrintVersionAction
from trashcli.fstab import Volumes, VolumesListing
from trashcli.trash import EX_OK, Clock, DirReader
from trashcli.trash_dirs_scanner import TopTrashDirRules


class EmptyCmd:
    def __init__(self,
                 argv0,  # type: str
                 out,  # type: TextIOWrapper
                 err,  # type: TextIOWrapper
                 volumes_listing,  # type: VolumesListing
                 now,  # type: () -> datetime
                 file_reader,  # type: TopTrashDirRules.Reader
                 dir_reader,  # type: DirReader
                 content_reader,  # type: ContentReader
                 file_remover,  # type: ExistingFileRemover
                 version,  # type: str
                 volumes,  # type: Volumes
                 ):
        self.volumes = volumes
        self.file_remover = file_remover
        self.dir_reader = dir_reader
        self.file_reader = file_reader
        self.volumes_listing = volumes_listing
        self.argv0 = argv0
        self.out = out
        self.err = err
        self.version = version
        self.now = now
        self.content_reader = content_reader
        self.parser = Parser()
        self.program_name = os.path.basename(argv0)
        errors = Errors(self.program_name, self.err)
        clock = Clock(self.now, errors)
        console = Console(self.program_name, self.out, self.err)

        self.actions = {
            Action.empty: EmptyAction(clock,
                                      self.file_remover,
                                      self.volumes_listing,
                                      self.file_reader,
                                      self.volumes,
                                      self.dir_reader,
                                      self.content_reader,
                                      console),
            Action.print_version: PrintVersionAction(self.out,
                                                     self.version,
                                                     self.program_name),
            Action.print_time: PrintTimeAction(self.out, clock),
        }

    def run_cmd(self, args, environ, uid):
        parsed = self.parser.parse(is_input_interactive(), args)
        self.actions[parsed.action].run_action(parsed, environ, uid)
        return EX_OK
