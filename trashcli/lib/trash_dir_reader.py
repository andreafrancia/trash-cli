from __future__ import absolute_import

import os
from trashcli.fslib.real.entries_if_dir_exists import EntriesIfDirExists

from trashcli.compat import Protocol
from abc import abstractmethod
from typing import List


class TrashDirReader:

    def __init__(self,
                 fs,  # type: TrashDirReaderFs
                 ):
        self.fs = fs

    def list_orphans(self, path):
        info_dir = os.path.join(path, 'info')
        files_dir = os.path.join(path, 'files')
        for entry in self._entries_if_dir_exists(files_dir):
            trashinfo_path = os.path.join(info_dir, entry + '.trashinfo')
            file_path = os.path.join(files_dir, entry)
            if not self.fs.path_exists(trashinfo_path):
                yield file_path

    def list_trashinfo(self, path):
        info_dir = os.path.join(path, 'info')
        for entry in self._entries_if_dir_exists(info_dir):
            if entry.endswith('.trashinfo'):
                yield os.path.join(info_dir, entry)

    def _entries_if_dir_exists(self, path):
        return EntriesIfDirExists(self.fs).entries_if_dir_exists(path)


class TrashDirReaderFs(Protocol):
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
