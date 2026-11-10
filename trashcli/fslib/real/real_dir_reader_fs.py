from __future__ import absolute_import

from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.path_exists import PathExists
from trashcli.fslib.real.real_entries_if_dir_exists import EntriesIfDirExistsImpl


class RealDirReaderFs(PathExists):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def entries_if_dir_exists(self, path):
        return EntriesIfDirExistsImpl(self.fs).entries_if_dir_exists(path)

    def path_exists(self, path):  # type: (str) -> bool
        return self.fs.path_exists(path)
