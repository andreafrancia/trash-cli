from abc import abstractmethod

from trashcli.compat import Protocol


class RestoreWriterFs(Protocol):
    @abstractmethod
    def mkdirs(self, path):  # type: (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def move(self, path, dest):  # type: (str, str) -> None
        raise NotImplementedError()

    @abstractmethod
    def remove_file(self, path):  # type: (str) -> None
        raise NotImplementedError()
