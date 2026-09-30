from abc import abstractmethod

from trashcli.compat import Protocol


class RemoveFileIfExists(Protocol):
    @abstractmethod
    def remove_file_if_exists(self, path):
        raise NotImplementedError()
