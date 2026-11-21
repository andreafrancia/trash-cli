from abc import abstractmethod

from trashcli.compat import Protocol


class ShutilMove(Protocol):
    @abstractmethod
    def shutil_move(self, src, dst):  # type: (str, str) -> None
        raise NotImplementedError
