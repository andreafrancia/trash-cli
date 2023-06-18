# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import TextIO, Callable

from trashcli.lib.my_input import Input
from trashcli.lib.print_version import PrintVersionAction, PrintVersionArgs
from trashcli.restore.args import RunRestoreArgs
from trashcli.restore.file_system import RestoreReadFileSystem, \
    RestoreWriteFileSystem, ReadCwd
from trashcli.restore.handler import HandlerImpl
from trashcli.restore.real_output import RealOutput
from trashcli.restore.restore_arg_parser import RestoreArgParser
from trashcli.restore.restorer import Restorer
from trashcli.restore.run_restore_action import RunRestoreAction, Handler
from trashcli.restore.trashed_files import TrashedFiles


class RestoreCmd(object):
    @staticmethod
    def make(stdout,  # type: TextIO
             stderr,  # type: TextIO
             exit,  # type: Callable[[int], None]
             input,  # type: Input
             version,  # type: str
             trashed_files,  # type: TrashedFiles
             read_fs,  # type: RestoreReadFileSystem
             write_fs,  # type: RestoreWriteFileSystem
             read_cwd,  # type: ReadCwd
             ):  # type: (...) -> RestoreCmd
        restorer = Restorer(read_fs, write_fs)
        output = RealOutput(stdout, stderr, exit)
        handler = HandlerImpl(input, read_cwd, restorer, output)
        return RestoreCmd(stdout, version, trashed_files, read_cwd, handler)

    def __init__(self,
                 stdout,  # type: TextIO
                 version,  # type: str
                 trashed_files,  # type: TrashedFiles
                 read_cwd,  # type: ReadCwd
                 handler,  # type: Handler
                 ):
        self.read_cwd = read_cwd
        self.parser = RestoreArgParser()
        self.run_restore_action = RunRestoreAction(handler,
                                                   trashed_files)
        self.print_version_action = PrintVersionAction(stdout,
                                                       version)

    def run(self, argv):
        args = self.parser.parse_restore_args(argv,
                                              self.read_cwd.getcwd_as_realpath())

        if isinstance(args, RunRestoreArgs):
            self.run_restore_action.run_action(args)
        elif isinstance(args, PrintVersionArgs):
            self.print_version_action.run_action(args)
