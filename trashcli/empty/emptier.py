from trashcli.empty.console import Console
from trashcli.empty.delete_according_date import DeleteAccordingDate
from trashcli.empty.errors import Errors
from trashcli.empty.file_remove_with_error_handling import \
    FileRemoveWithErrorHandling
from trashcli.fs import FileRemover
from trashcli.trash import TrashDirReader, path_of_backup_copy
from trashcli.trash_dirs_scanner import only_found, TrashDir


class Emptier:
    def __init__(self, delete_mode, trash_dir_reader, file_remover, errors
                 ):  # type: (DeleteAccordingDate, TrashDirReader, FileRemover, Errors) -> None
        self.console = Console(errors)
        self.file_remover_with_error = FileRemoveWithErrorHandling(file_remover,
                                                                   self.console)
        self.delete_mode = delete_mode
        self.trash_dir_reader = trash_dir_reader

    def do_empty(self, trash_dirs, environ, parsed_days):
        for trash_dir in only_found(trash_dirs):  # type: TrashDir
            for trash_info_path in self.trash_dir_reader.list_trashinfo(
                    trash_dir.path):
                if self.delete_mode.ok_to_delete(trash_info_path, environ,
                                                 parsed_days):
                    backup_copy = path_of_backup_copy(trash_info_path)
                    self.file_remover_with_error.remove_file_if_exists2(
                        backup_copy)
                    self.file_remover_with_error.remove_file2(trash_info_path)
            for orphan in self.trash_dir_reader.list_orphans(
                    trash_dir.path):
                self.file_remover_with_error.remove_file2(orphan)
