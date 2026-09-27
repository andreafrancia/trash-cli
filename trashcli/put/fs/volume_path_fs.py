from abc import abstractmethod

from trashcli.compat import Protocol


class VolumePathFs(Protocol):
    @abstractmethod
    def is_root_volume(self, volume_path):  # type: (str) -> bool
        raise NotImplementedError()

    @abstractmethod
    def is_outside_of(self, path, volume_path):  # type: (str, str) -> bool
        raise NotImplementedError()
