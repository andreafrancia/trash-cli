# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from abc import abstractmethod

from trashcli.compat import Protocol


class MountPointListFs(Protocol):
    @abstractmethod
    def list_mount_points(self):
        raise NotImplementedError()
