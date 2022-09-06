from trashcli.trash import path_of_backup_copy


class CleanableTrashcan:
    def __init__(self, file_remover):
        self._file_remover = file_remover

    def delete_orphan(self, path_to_backup_copy):
        self._file_remover.remove_file(path_to_backup_copy)

    def delete_trashinfo_and_backup_copy(self, trashinfo_path):
        backup_copy = path_of_backup_copy(trashinfo_path)
        self._file_remover.remove_file_if_exists(backup_copy)
        self._file_remover.remove_file(trashinfo_path)
