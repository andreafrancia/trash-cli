from abc import abstractmethod

from trashcli.compat import Protocol


class PathIsDir(Protocol):
    @abstractmethod
    def path_isdir(self, path):  # type: (str) -> bool
        raise NotImplementedError()
