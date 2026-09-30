from abc import abstractmethod

from trashcli.compat import Protocol


class PathExists(Protocol):
    @abstractmethod
    def exists(self, path):
        raise NotImplementedError()
