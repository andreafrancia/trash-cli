from abc import abstractmethod

from trashcli.compat import Protocol


class AtomicWrite(Protocol):
    @abstractmethod
    def atomic_write(self, path, content):
        raise NotImplementedError()

    @abstractmethod
    def open_for_write_in_exclusive_and_create_mode(self, path):
        raise NotImplementedError()
