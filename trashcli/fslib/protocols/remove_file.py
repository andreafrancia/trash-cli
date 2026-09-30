from abc import abstractmethod

from trashcli.compat import Protocol


class RemoveFile(Protocol):
    @abstractmethod
    def remove_file(self, path):
        raise NotImplementedError()
