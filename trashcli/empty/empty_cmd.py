import os
from datetime import datetime
from typing import TextIO, Callable, Mapping

from trashcli.empty.clock import Clock
from trashcli.empty.console import Console
from trashcli.empty.empty_action import EmptyAction, EmptyActionArgs
from trashcli.empty.errors import Errors
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.empty.is_input_interactive import is_input_interactive
from trashcli.empty.parser import Parser
from trashcli.empty.print_time_action import PrintTimeAction, PrintTimeArgs
from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.fslib.protocols.volume_of import VolumeOfFs
from trashcli.lib.exit_codes import EX_OK
from trashcli.lib.print_version import PrintVersionAction, PrintVersionArgs


class EmptyCmd:
    def __init__(self,
                 argv0,  # type: str
                 out,  # type: TextIO
                 err,  # type: TextIO
                 environ,  # type: Mapping[str, str]
                 volumes_listing,  # type: VolumesListing
                 now,  # type: Callable[[], datetime]
                 fs,  # type: Fs
                 geteuid,  # type: Callable[[], int]
                 version,  # type: str
                 volumes,  # type: VolumeOfFs
                 ):
        self.volumes = volumes
        self.volumes_listing = volumes_listing
        self.argv0 = argv0
        self.out = out
        self.err = err
        self.version = version
        self.now = now
        self.parser = Parser()
        self.program_name = os.path.basename(argv0)
        errors = Errors(self.program_name, self.err)
        clock = Clock(self.now, errors)
        console = Console(self.program_name, self.out, self.err)
        self.empty_action = EmptyAction(clock,
                                        volumes_listing=self.volumes_listing,
                                        file_reader=fs,
                                        volumes=self.volumes,
                                        dir_reader=FileSystemDirReader(fs),
                                        content_reader=fs,
                                        console=console,
                                        environ=environ,
                                        geteuid=geteuid,
                                        fs=fs,
                                        )
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
