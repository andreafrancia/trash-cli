from abc import abstractmethod

from trashcli.compat import Protocol


class IsSymLink(Protocol):
    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError
