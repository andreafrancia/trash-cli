from abc import abstractmethod

from trashcli.compat import Protocol


class ReadCwdFs(Protocol):
    @abstractmethod
    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError()
