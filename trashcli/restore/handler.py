from __future__ import print_function
from __future__ import unicode_literals

from typing import List

from trashcli.lib.my_input import Input
from trashcli.restore.file_system import ReadCwd
from trashcli.restore.output import Output
from trashcli.restore.output_recorder import OutputRecorder
from trashcli.restore.restore_asking_the_user import RestoreAskingTheUser
from trashcli.restore.restorer import Restorer
from trashcli.restore.run_restore_action import Handler
from trashcli.restore.trashed_file import TrashedFile


class HandlerImpl(Handler):
    def __init__(self,
                 input,  # type: Input
                 cwd,  # type: ReadCwd
                 restorer,  # type: Restorer
                 output,  # type: Output
                 ):
        self.input = input
        self.cwd = cwd
        self.restorer = restorer
        self.output = output

    def handle_trashed_files(self,
                             trashed_files,  # type: List[TrashedFile]
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
