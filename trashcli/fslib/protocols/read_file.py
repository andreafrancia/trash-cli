from abc import abstractmethod

from trashcli.compat import Protocol


class ReadFile(Protocol):
    @abstractmethod
    def read_file(self, path):
        raise NotImplementedError()
