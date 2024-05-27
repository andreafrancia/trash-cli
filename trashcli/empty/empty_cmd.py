import os
from datetime import datetime

from typing import Callable
from typing import TextIO

from trashcli.empty.clock import Clock
from trashcli.empty.console import Console
from trashcli.empty.empty_action import EmptyAction
from trashcli.empty.empty_action import EmptyActionArgs
from trashcli.empty.errors import Errors
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.is_input_interactive import is_input_interactive
from trashcli.empty.parser import Parser
from trashcli.empty.print_time_action import PrintTimeAction
from trashcli.empty.print_time_action import PrintTimeArgs
from trashcli.fs import FileReader
from trashcli.fstab.mount_points_listing import MountPointsListing
from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.dir_reader import DirReader
from trashcli.lib.exit_codes import EX_OK
from trashcli.lib.print_version import PrintVersionAction
from trashcli.lib.print_version import PrintVersionArgs
from trashcli.trash_dirs_scanner import TopTrashDirRules


class EmptyCmd:
    def __init__(self,
                 argv0,  # type: str
                 out,  # type: TextIO
                 err,  # type: TextIO
                 now,  # type: Callable[[], datetime]
                 file_reader,  # type: TopTrashDirRules.Reader
                 dir_reader,  # type: DirReader
                 content_reader,  # type: FileReader
                 file_remover,  # type: ExistingFileRemover
                 version,  # type: str
                 volumes,  # type: VolumeOf
                 mount_point_listing,  # type: MountPointsListing
                 ):
        self.argv0 = argv0
        program_name = os.path.basename(argv0)
        errors = Errors(program_name, err)
        clock = Clock(now, errors)
        console = Console(program_name, out, err)
        self.empty_action = EmptyAction(clock, file_remover,
                                        file_reader, volumes, dir_reader,
                                        content_reader, console,
                                        mount_point_listing)
        self.print_version_action = PrintVersionAction(out, version)
        self.print_time_action = PrintTimeAction(out, clock)

    def run_cmd(self, args, environ, uid):
        args = Parser().parse(
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
