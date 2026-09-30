from abc import abstractmethod

from trashcli.compat import Protocol


class ContentsOf(Protocol):
    @abstractmethod
    def contents_of(self, path):
        raise NotImplementedError()
