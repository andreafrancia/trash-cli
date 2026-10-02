from abc import abstractmethod

from trashcli.compat import Protocol


class IsMountFs(Protocol):
    @abstractmethod
    def is_mount(self, path):
        raise NotImplementedError
