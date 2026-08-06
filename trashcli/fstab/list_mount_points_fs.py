from abc import abstractmethod

from trashcli.compat import Protocol


class OsMountPointsFs(Protocol):
    @abstractmethod
    def list_os_mount_points(self):
        raise NotImplementedError()
