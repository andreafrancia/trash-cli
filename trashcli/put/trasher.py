from trashcli.put.context import Context
from trashcli.put.core.trash_result import TrashResult
from trashcli.put.core.trashee import should_skipped_by_specs
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.fs.fs import Fs
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.user import User
from trashcli.put.user import user_replied_no


class Trasher:
    def __init__(self,
                 file_trasher,  # type: FileTrasher
                 user,  # type: User
                 reporter,  # type: TrashPutReporter
                 fs,  # type: Fs
                 ):
        self.file_trasher = file_trasher
        self.user = user
        self.reporter = reporter
        self.fs = fs

    def trash_single(self,
                     path,  # type: str
                     context,  # type: Context
                     ):
        """
        Trash a file in the appropriate trash directory.
        If the file belong to the same volume of the trash home directory it
        will be trashed in the home trash directory.
        Otherwise it will be trashed in one of the relevant volume trash
        directories.

        Each volume can have two trash directories, they are
            - $volume/.Trash/$uid
            - $volume/.Trash-$uid

        Firstly the software attempt to trash the file in the first directory
        then try to trash in the second trash directory.
        """

        if should_skipped_by_specs(path):
            self.reporter.unable_to_trash_dot_entries(path, context.log_data)
            return TrashResult.Failure

        if not self.fs.lexists(path):
            if context.mode.can_ignore_not_existent_path():
                return TrashResult.Success
            else:
                self.reporter.unable_to_trash_file_non_existent(path,
                                                                context.log_data)
                return TrashResult.Failure

        if context.mode.should_we_ask_to_the_user(self.fs.is_accessible(path)):
            reply = self.user.ask_user_about_deleting_file(context.program_name,
                                                           path)
            if reply == user_replied_no:
                return TrashResult.Success

        return self.file_trasher.trash_file(path, context)
