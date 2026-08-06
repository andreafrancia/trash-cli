import os
from typing import MutableMapping, Optional, Iterable

from trashcli.fstab.volumes import Volumes


class FakeVolumes(Volumes):
    def __init__(self, volumes=None):
        self.volumes = volumes or []

    def list_volumes(self,
                     environ=None,  # type: Optional[MutableMapping[str,str]]
                     ):  # type: (...) -> Iterable[str]
        return self.volumes

    def set_volumes(self, volumes_list):
        self.volumes = volumes_list

    def volume_of(self, path):  # type: (str) -> str
        while path != os.path.dirname(path):
            if self.is_mount(path):
                break
            path = os.path.dirname(path)
        return path

    def is_mount(self, path):
        return path in self.volumes

    def add_volume(self, path):
        self.volumes.append(path)
