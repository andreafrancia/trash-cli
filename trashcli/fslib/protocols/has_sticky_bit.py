from abc import abstractmethod

from trashcli.compat import Protocol


class HasStickyBit(Protocol):
    @abstractmethod
    def has_sticky_bit(self, path):  # type: (str) -> bool
        raise NotImplementedError
