# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
from trashcli.rm.file_remover import FileRemover
from trashcli.lib.path_of_backup_copy import path_of_backup_copy


class CleanableTrashcan:
    def __init__(self,
                 file_remover, # type: FileRemover
                 ):
        self._file_remover = file_remover

    def delete_trash_info_and_backup_copy(self, trash_info_path):
        backup_copy = path_of_backup_copy(trash_info_path)
        self._file_remover.remove_file_if_exists(backup_copy)
        self._file_remover.remove_file2(trash_info_path)
