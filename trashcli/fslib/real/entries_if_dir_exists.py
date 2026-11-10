from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol


class EntriesIfDirExists:
    def __init__(self,
                 fs,  # type: RealEntriesIfDirExistsFs
                 ):  # type: (...) -> None
        self.fs = fs

    def entries_if_dir_exists(self, path):
        if self.fs.path_exists(path):
            for entry in self.fs.listdir(path):
                yield entry


class RealEntriesIfDirExistsFs(Protocol):
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
