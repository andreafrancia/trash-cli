from abc import abstractmethod

from trashcli.compat import Protocol


class WriteFile(Protocol):
    @abstractmethod
    def write_file(self, name, contents):
        raise NotImplementedError()
