import os
from datetime import datetime
from typing import TextIO, Callable

from trashcli.empty.clock import Clock
from trashcli.empty.console import Console
from trashcli.empty.empty_action import EmptyAction, EmptyActionArgs
from trashcli.empty.errors import Errors
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.is_input_interactive import is_input_interactive
from trashcli.empty.parser import Parser
from trashcli.empty.print_time_action import PrintTimeAction, PrintTimeArgs
from trashcli.fs import ContentsOf
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.dir_reader import DirReader
from trashcli.lib.exit_codes import EX_OK
from trashcli.lib.print_version import PrintVersionAction, PrintVersionArgs
from trashcli.trash_dirs_scanner import TopTrashDirRules


class EmptyCmd:
    def __init__(self,
                 argv0,  # type: str
                 out,  # type: TextIO
                 err,  # type: TextIO
                 volumes_listing,  # type: VolumesListing
                 now,  # type: Callable[[], datetime]
                 file_reader,  # type: TopTrashDirRules.Reader
                 dir_reader,  # type: DirReader
                 content_reader,  # type: ContentsOf
                 file_remover,  # type: ExistingFileRemover
                 version,  # type: str
                 volumes,  # type: VolumeOf
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
        self.empty_action = EmptyAction(clock,
                                        self.file_remover,
                                        self.volumes_listing,
                                        self.file_reader,
                                        self.volumes,
                                        self.dir_reader,
                                        self.content_reader,
                                        console)
        self.print_version_action = PrintVersionAction(self.out,
                                                       self.version)
        self.print_time_action = PrintTimeAction(self.out, clock)

    def run_cmd(self, args, environ, uid):
        args = self.parser.parse(
            default_is_interactive=is_input_interactive(),
            args=args,
            argv0=self.argv0,
            environ=environ,
            uid=uid)

        if type(args) is PrintVersionArgs:
            return self.print_version_action.run_action(args)
        elif type(args) is EmptyActionArgs:
            return self.empty_action.run_action(args)
        elif type(args) is PrintTimeArgs:
            return self.print_time_action.run_action(args)

        return EX_OK
