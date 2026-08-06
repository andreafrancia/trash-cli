from abc import abstractmethod

from trashcli.compat import Protocol


class IsMount(Protocol):
    @abstractmethod
    def is_mount(self, path):
        raise NotImplementedError
