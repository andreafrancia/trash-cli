from abc import abstractmethod

from trashcli.compat import Protocol


class Move(Protocol):
    @abstractmethod
    def move(self, path, dest):
        raise NotImplementedError()
