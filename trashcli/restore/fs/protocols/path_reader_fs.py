from abc import abstractmethod

from trashcli.compat import Protocol


class PathReaderFs(Protocol):
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()

    @abstractmethod
    def path_lexists(self, path):  # type: (str) -> bool
        return self.path_exists(path)

    @abstractmethod
    def path_isdir(self, path):  # type: (str) -> bool
        return False
