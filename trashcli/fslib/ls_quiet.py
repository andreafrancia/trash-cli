from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol


class LsQuiet:
    def __init__(self,
                 fs,  # type: LsQuietFs
                 ):  # type: (...) -> None
        self.fs = fs

    def list_if_exists(self, path):
        if self.fs.path_exists(path):
            for entry in self.fs.listdir(path):
                yield entry


class LsQuietFs(Protocol):
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
