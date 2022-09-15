from trashcli.empty.file_remove_with_error_handling import \
    FileRemoveWithErrorHandling
from trashcli.trash import path_of_backup_copy


class CleanableTrashcan:
    def __init__(self, file_remover): # type: (FileRemoveWithErrorHandling) -> None
        self._file_remover = file_remover

    def delete_orphan(self, path_to_backup_copy):
        self._file_remover.remove_file2(path_to_backup_copy)

    def delete_trash_info_and_backup_copy(self, trash_info_path):
        backup_copy = path_of_backup_copy(trash_info_path)
        self._file_remover.remove_file_if_exists2(backup_copy)
        self._file_remover.remove_file2(trash_info_path)
