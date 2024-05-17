from abc import abstractmethod

from trashcli.compat import Protocol


class VolumeOf(Protocol):
    @abstractmethod
    def volume_of(self, path):
        raise NotImplementedError()
