from __future__ import print_function
from __future__ import unicode_literals

from typing import TextIO, Callable

from trashcli.restore.file_system import ReadCwd
from trashcli.restore.restore_asking_the_user import RestoreAskingTheUser
from trashcli.restore.restorer import Restorer
from trashcli.restore.run_restore_action import Handler


class HandlerImpl(Handler):
    def __init__(self,
                 stdout,  # type: TextIO
                 stderr,  # type: TextIO
                 exit,  # type: Callable[[int], None]
                 input,  # type: Callable[[str], str]
                 cwd,  # type: ReadCwd
                 restorer,  # type: Restorer
                 ):
        self.stdout = stdout
        self.stderr = stderr
        self.exit = exit
        self.input = input
        self.cwd = cwd
        self.restorer = restorer

    def handle_trashed_files(self,
                             trashed_files,
                             overwrite,  # type: bool
                             ):
        if not trashed_files:
            self.report_no_files_found()
        else:
            for i, trashedfile in enumerate(trashed_files):
                self.println("%4d %s %s" % (i,
                                            trashedfile.deletion_date,
                                            trashedfile.original_location))
            self.restore_asking_the_user(trashed_files, overwrite)

    def restore_asking_the_user(self, trashed_files, overwrite=False):
        restore_asking_the_user = RestoreAskingTheUser(self.input,
                                                       self.println,
                                                       self.restorer,
                                                       self.die)
        restore_asking_the_user.restore_asking_the_user(trashed_files,
                                                        overwrite)

    def die(self, error):
        self.printerr(error)
        self.exit(1)

    def report_no_files_found(self):
        self.println(
            "No files trashed from current dir ('%s')" % self.cwd.getcwd_as_realpath())

    def println(self, line):
        print("%s" % line, file=self.stdout)

    def printerr(self, msg):
        print("%s" % msg, file=self.stderr)
