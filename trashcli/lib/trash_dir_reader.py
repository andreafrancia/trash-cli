from __future__ import absolute_import

import os
from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol
from trashcli.fslib.ls_quiet import LsQuiet


class TrashDirReader:

    def __init__(self,
                 fs,  # type: TrashDirReaderFs
                 ):
        self.fs = fs

    def list_orphans(self, path):
        info_dir = os.path.join(path, 'info')
        files_dir = os.path.join(path, 'files')
        for entry in self._list_if_exists(files_dir):
            trashinfo_path = os.path.join(info_dir, entry + '.trashinfo')
            file_path = os.path.join(files_dir, entry)
            if not self.fs.path_exists(trashinfo_path):
                yield file_path

    def list_trashinfo(self, path):
        info_dir = os.path.join(path, 'info')
        for entry in self._list_if_exists(info_dir):
            if entry.endswith('.trashinfo'):
                yield os.path.join(info_dir, entry)

    def _list_if_exists(self, path):
        return LsQuiet(self.fs).list_if_exists(path)


class TrashDirReaderFs(Protocol):
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
