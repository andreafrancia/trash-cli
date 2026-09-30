from abc import abstractmethod

from trashcli.compat import Protocol


class IsWorldWritable(Protocol):
    @abstractmethod
    def is_world_writable(self, path):  # type: (str) -> bool
        raise NotImplementedError
