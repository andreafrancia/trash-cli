from trashcli.restore.restore_asking_the_user import RestoreAskingTheUser
from trashcli.restore.run_restore_action import Handler
from trashcli.restore.restorer import Restorer


class HandlerImpl(Handler):
    def __init__(self, stdout, stderr, exit, input, fs):
        self.stdout = stdout
        self.stderr = stderr
        self.exit = exit
        self.input = input
        self.fs = fs

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
                                                       self.restore,
                                                       self.die)
        restore_asking_the_user.restore_asking_the_user(trashed_files,
                                                        overwrite)

    def die(self, error):
        self.printerr(error)
        self.exit(1)

    def restore(self, trashed_file, overwrite=False):
        restorer = Restorer(self.fs)
        restorer.restore_trashed_file(trashed_file, overwrite)

    def report_no_files_found(self):
        self.println(
            "No files trashed from current dir ('%s')" % self.fs.getcwd_as_realpath())

    def println(self, line):
        self.stdout.write(line + '\n')

    def printerr(self, msg):
        self.stderr.write('%s\n' % msg)
