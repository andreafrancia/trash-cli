# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import Callable
from typing import List
from typing import TextIO
from typing import Any
try:
    from typing_extensions import Self
except ImportError:
    Self = Any

from trashcli.fs import ReadCwd
from trashcli.fstab.volumes import Volumes
from trashcli.lib.environ import Environ
from trashcli.lib.my_input import Input
from trashcli.lib.print_version import PrintVersionAction
from trashcli.lib.print_version import PrintVersionArgs
from trashcli.put.fs.fs import Fs
from trashcli.restore.args import RunRestoreArgs
from trashcli.restore.restore_arg_parser import RestoreArgParser
from trashcli.restore.restore_logger import RestoreLogger
from trashcli.restore.run_restore_action import RunRestoreAction


class RestoreCmd(object):
    def __init__(self,
                 stdout,  # type: TextIO
                 stderr,  # type: TextIO
                 exit,  # type: Callable[[int], None]
                 user_input,  # type: Input
                 version,  # type: str
                 volumes,  # type: Volumes
                 uid,  # type: int
                 environ,  # type: Environ
                 logger,  # type: RestoreLogger
                 read_cwd,  # type: ReadCwd
                 fs,  # type: Fs
                 ):
        self.read_cwd = read_cwd
        self.parser = RestoreArgParser()
        self.run_restore_action = RunRestoreAction(stdout, stderr, exit, user_input,
                                              volumes, uid, environ, logger,
                                              read_cwd, fs)
        self.print_version_action = PrintVersionAction(stdout, version)

    def run(self,  # type: Self
            argv,
            ):
        args = self.parser.parse_restore_args(
            argv, self.read_cwd.getcwd_as_realpath())

        if isinstance(args, RunRestoreArgs):
            self.run_restore_action.run_action(args)
        elif isinstance(args, PrintVersionArgs):
            self.print_version_action.run_action(args)
