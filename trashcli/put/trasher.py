import os

from typing import Dict

from trashcli.put.access import Access
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.parser import mode_force, mode_interactive
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_result import TrashResult
from trashcli.put.user import User, user_replied_no


class Trasher:
    def __init__(self,
                 file_trasher, # type: FileTrasher
                 user, # type: User
                 access, # type: Access
                 reporter, # type: TrashPutReporter
                 ):
        self.file_trasher = file_trasher
        self.user = user
        self.access = access
        self.reporter = reporter

    def trash(self,
              path,
              user_trash_dir,
              result,  # type: TrashResult
              mode,
              forced_volume,
              program_name,
              verbose,
              environ,  # type: Dict[str, str]
              uid, # type: int
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

        if self._should_skipped_by_specs(path):
            self.reporter.unable_to_trash_dot_entries(path, program_name)
            return result

        if mode == mode_force and not self.access.is_accessible(path):
            return result

        if mode == mode_interactive and self.access.is_accessible(path):
            reply = self.user.ask_user_about_deleting_file(program_name, path)
            if reply == user_replied_no:
                return result

        return self.file_trasher.trash_file(path,
                                            forced_volume,
                                            user_trash_dir,
                                            result,
                                            environ,
                                            uid,
                                            program_name,
                                            verbose,
                                            )

    def _should_skipped_by_specs(self, file):
        basename = os.path.basename(file)
        return (basename == ".") or (basename == "..")
