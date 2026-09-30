from abc import abstractmethod

from trashcli.compat import Protocol


class RemoveFile2(Protocol):
    @abstractmethod
    def remove_file2(self, path):
        raise NotImplementedError()
