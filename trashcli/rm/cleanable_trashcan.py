# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
from abc import abstractmethod
from typing import Optional

from trashcli.compat import Protocol
from trashcli.lib.path_of_backup_copy import path_of_backup_copy


class RemoverFs(Protocol):
    @abstractmethod
    def check_trash_dir(self, trash_dir, volume, uid):
        # type: (str, str, Optional[int]) -> os.stat_result
        raise NotImplementedError()

    @abstractmethod
    def remove_if_exists(self, checked_dir, path):  # type: (os.stat_result, str) -> None
        raise NotImplementedError()


class CleanableTrashcan:
    def __init__(self,
                 file_remover, # type: RemoverFs
                 ):
        self._file_remover = file_remover

    def delete_trash_info_and_backup_copy(self, checked_dir, trash_info_path):
        backup_copy = path_of_backup_copy(trash_info_path)
        self._file_remover.remove_if_exists(checked_dir, backup_copy)
        self._file_remover.remove_if_exists(checked_dir, trash_info_path)
