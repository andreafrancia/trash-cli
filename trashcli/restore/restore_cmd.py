# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy

from trashcli.restore.file_system import RestoreFileSystem
from trashcli.restore.handler import HandlerImpl
from trashcli.restore.run_restore_action import RunRestoreAction, Handler
from trashcli.restore.trashed_file import TrashedFiles
from trashcli.restore.parse_restore_args import parse_restore_args, \
    PrintVersionArgs, RunRestoreArgs
from trashcli.lib.print_version import PrintVersionAction


class RestoreCmd(object):
    @staticmethod
    def make(stdout, stderr, exit, input, version, trashed_files,
             mount_points, fs):
        handler = HandlerImpl(stdout, stderr, exit, input, fs)
        return RestoreCmd(stdout, version, trashed_files, mount_points, fs,
                          handler)

    def __init__(self,
                 stdout,
                 version,
                 trashed_files,  # type: TrashedFiles
                 mount_points,
                 fs,  # type: RestoreFileSystem
                 handler,  # type: Handler
                 ):
        self.stdout = stdout
        self.version = version
        self.fs = fs
        self.trashed_files = trashed_files
        self.mount_points = mount_points
        self.handler = handler
        self.run_restore_action = RunRestoreAction(self.handler,
                                                   self.trashed_files,
                                                   self.mount_points)
        self.print_version_action = PrintVersionAction(self.stdout,
                                                       self.version)

    def run(self, argv):
        args = parse_restore_args(argv, self.fs.getcwd_as_realpath())

        if isinstance(args, RunRestoreArgs):
            self.run_restore_action.run_action(args)
        elif isinstance(args, PrintVersionArgs):
            self.print_version_action.run_action(args)
