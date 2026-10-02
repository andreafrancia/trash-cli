from abc import abstractmethod

from trashcli.compat import Protocol


class VolumeOfFs(Protocol):
    def volume_of(self, path):
        raise NotImplementedError()
