from abc import abstractmethod

from trashcli.compat import Protocol


class FileSize(Protocol):
    @abstractmethod
    def file_size(self, path):
        raise NotImplementedError()
