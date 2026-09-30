from abc import abstractmethod

from trashcli.compat import Protocol


class MkDirs(Protocol):
    @abstractmethod
    def mkdirs(self, path):
        raise NotImplementedError()
