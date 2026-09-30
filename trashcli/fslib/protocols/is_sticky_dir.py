from abc import abstractmethod

from trashcli.compat import Protocol


class IsStickyDir(Protocol):
    @abstractmethod
    def is_sticky_dir(self, path):  # type: (str) -> bool
        raise NotImplementedError
