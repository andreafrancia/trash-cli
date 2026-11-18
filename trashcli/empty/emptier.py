# Copyright (C) 2022 Andrea Francia Bereguardo(PV) Italy
import os
from typing import Iterable, Tuple

from trashcli.empty.console import Console
from trashcli.empty.delete_according_date import DeleteAccordingDate
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.trash_dirs_scanner import TrashDir, only_found


class Emptier:
    def __init__(self, delete_mode, trash_dir_reader, file_remover, console
                 ):  # type: (DeleteAccordingDate, TrashDirReader, ExistingFileRemover, Console) -> None
        self.console = console
        self.file_remover = file_remover
        self.delete_mode = delete_mode
        self.trash_dir_reader = trash_dir_reader

    def do_empty(self,
                 trash_dirs,  # type: Iterable[TrashDir]
                 environ,  # type: dict
                 parsed_days,  # type: int
                 dry_run,  # type: bool
                 verbose,  # type: int
                 ):  # type: (...) -> None
        for checked_dir, path in self.files_to_delete(trash_dirs, environ, parsed_days):
            if dry_run:
                self.console.print_dry_run(path)
            else:
                if verbose:
                    self.console.print_removing(path)
                try:
                    self.file_remover.remove_if_exists(checked_dir, path)
                except OSError:
                    self.console.print_cannot_remove_error(path)

    def files_to_delete(self,
                        trash_dirs,  # type: Iterable[TrashDir]
                        environ,  # type: dict
                        parsed_days,  # type: int
                        ):  # type: (...) -> Iterable[Tuple[os.stat_result, str]]
        for trash_dir in only_found(trash_dirs):  # type: TrashDir
            try:
                # each removal checks that it still happens inside this dir
                checked_dir = self.file_remover.check_trash_dir(
                    trash_dir.path, trash_dir.volume, trash_dir.uid)
            except OSError:
                continue
            for trash_info_path in self.trash_dir_reader.list_trashinfo(
                    trash_dir.path):
                if self.delete_mode.ok_to_delete(trash_info_path, environ,
                                                 parsed_days):
                    yield checked_dir, path_of_backup_copy(trash_info_path)
                    yield checked_dir, trash_info_path
