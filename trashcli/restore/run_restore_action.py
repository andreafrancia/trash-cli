from __future__ import print_function
from __future__ import unicode_literals

import os
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import TextIO

from trashcli.fs import ReadCwd
from trashcli.fstab.volumes import Volumes
from trashcli.lib.environ import Environ
from trashcli.lib.my_input import Input
from trashcli.put.fs.fs import Fs
from trashcli.restore.args import RunRestoreArgs
from trashcli.restore.output_recorder import OutputRecorder
from trashcli.restore.real_output import RealOutput
from trashcli.restore.restore_asking_the_user import RestoreAskingTheUser
from trashcli.restore.restore_logger import RestoreLogger
from trashcli.restore.restorer import Restorer
from trashcli.restore.sort_method import sort_files
from trashcli.restore.trashed_file import TrashedFile
from trashcli.restore.trashed_files import TrashedFiles


class RunRestoreAction:
    def __init__(self,
                 stdout,  # type: TextIO
                 stderr,  # type: TextIO
                 exit,  # type: Callable[[int], None]
                 user_input,  # type: Input
                 volumes,  # type: Volumes
                 uid,  # type: int
                 environ,  # type: Environ
                 logger,  # type: RestoreLogger
                 read_cwd,  # type: ReadCwd
                 fs,  # type: Fs
                 ):
        self.stdout = stdout
        self.stderr = stderr
        self.exit = exit
        self.user_input = user_input
        self.volumes = volumes
        self.uid = uid
        self.environ = environ
        self.logger = logger
        self.read_cwd = read_cwd
        self.fs = fs

    def run_action(self, args,  # type: RunRestoreArgs
                   ):  # type: (...) -> None
        handler = _Handler(self.user_input, self.read_cwd, self.fs,
                           self.stdout, self.stderr, self.exit)
        trashed_files = self.all_files_trashed_from_path(args.path,
                                                         args.trash_dir)
        trashed_files = sort_files(args.sort, trashed_files)

        handler.handle_trashed_files(trashed_files,
                                     args.overwrite)

    def all_files_trashed_from_path(self,
                                    path,  # type: str
                                    trash_dir_from_cli,  # type: Optional[str]
                                    ):  # type: (...) -> Iterable[TrashedFile]
        trashed_files = TrashedFiles(self.volumes, self.uid, self.environ,
                                     self.fs, self.logger)
        for trashed_file in trashed_files.all_trashed_files(
                trash_dir_from_cli):
            if trashed_file.original_location_matches_path(path):
                yield trashed_file


def original_location_matches_path(trashed_file_original_location, path):
    if path == os.path.sep:
        return True
    if trashed_file_original_location.startswith(path + os.path.sep):
        return True
    return trashed_file_original_location == path


class _Handler:
    def __init__(self,
                 input,  # type: Input
                 cwd,  # type: ReadCwd
                 fs,  # type: Fs
                 stdout,  # type: TextIO
                 stderr,  # type: TextIO
                 exit,  # type: Callable[[int], None]
                 ):
        self.input = input
        self.cwd = cwd
        self.restorer = Restorer(fs)
        self.output = RealOutput(stdout, stderr, exit)

    def handle_trashed_files(self,
                             trashed_files,  # type: Iterable[TrashedFile]
                             overwrite,  # type: bool
                             ):
        if not trashed_files:
            self.report_no_files_found(self.cwd.getcwd_as_realpath())
        else:
            for i, trashed_file in enumerate(trashed_files):
                self.output.println("%4d %s %s" % (i,
                                                   trashed_file.deletion_date,
                                                   trashed_file.original_location))
            self.restore_asking_the_user(trashed_files, overwrite)

    def restore_asking_the_user(self, trashed_files, overwrite=False):
        my_output = OutputRecorder()
        restore_asking_the_user = RestoreAskingTheUser(self.input,
                                                       self.restorer,
                                                       my_output)
        restore_asking_the_user.restore_asking_the_user(trashed_files,
                                                        overwrite)
        my_output.apply_to(self.output)

    def report_no_files_found(self, directory):  # type: (str) -> None
        self.output.println(
            "No files trashed from current dir ('%s')" % directory)
