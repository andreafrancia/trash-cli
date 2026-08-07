from abc import abstractmethod

from trashcli.compat import Protocol


class FileReaderFs(Protocol):
    @abstractmethod
    def contents_of(self, path):
        raise NotImplementedError()
