from abc import abstractmethod

from trashcli.compat import Protocol


class Cal(Protocol):
    @abstractmethod
    def today(self):
        raise NotImplementedError
