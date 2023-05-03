import os
from typing import Callable, List

from trashcli.restore.parse_restore_args import RunRestoreArgs
from trashcli.restore.trashed_file import TrashedFiles


class RunRestoreAction:
    def __init__(self,
                 handler,  # type: 'Handler'
                 trashed_files,  # type: TrashedFiles
                 mount_points,  # type: Callable[[], List[str]]
                 ):
        self.handler = handler
        self.trashed_files = trashed_files
        self.mount_points = mount_points

    def run_action(self, args,  # type RunRestoreArgs
                   ): # type: (...) -> None
        trash_dir_from_cli = args.trash_dir
        trashed_files = list(self.all_files_trashed_from_path(
            args.path, trash_dir_from_cli))
        if args.sort == 'path':
            trashed_files = sorted(trashed_files,
                                   key=lambda
                                       x: x.original_location + str(
                                       x.deletion_date))
        elif args.sort == 'date':
            trashed_files = sorted(trashed_files,
                                   key=lambda x: x.deletion_date)

        self.handler.handle_trashed_files(trashed_files,
                                          args.overwrite)

    def all_files_trashed_from_path(self, path, trash_dir_from_cli):
        for trashed_file in self.trashed_files.all_trashed_files(
                self.mount_points(), trash_dir_from_cli):
            if original_location_matches_path(
                    trashed_file.original_location,
                    path):
                yield trashed_file


class Handler:
    def handle_trashed_files(self,
                             trashed_files,
                             overwrite,  # type: bool
                             ):
        raise NotImplementedError()


def original_location_matches_path(trashed_file_original_location, path):
    if path == os.path.sep:
        return True
    if trashed_file_original_location.startswith(path + os.path.sep):
        return True
    return trashed_file_original_location == path
