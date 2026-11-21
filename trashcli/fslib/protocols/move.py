from abc import abstractmethod

from trashcli.compat import Protocol


class Move(Protocol):
    @abstractmethod
    def move(self, src, dst):  # type: (str, str) -> None
        raise NotImplementedError()
