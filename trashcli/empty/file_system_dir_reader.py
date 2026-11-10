from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol
from trashcli.fslib.protocols.dir_reader_fs import DirReaderFs
from trashcli.fslib.real.real_entries_if_dir_exists import \
    RealEntriesIfDirExists


class FileSystemDirReader(DirReaderFs):
    def __init__(self, fs):  # type: (FileSystemDirReaderFs) -> None
        self.fs = fs

    def entries_if_dir_exists(self, path):
        return RealEntriesIfDirExists(self.fs).entries_if_dir_exists(path)

    def path_exists(self, path):  # type: (str) -> bool
        return self.fs.path_exists(path)


class FileSystemDirReaderFs(Protocol):
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
