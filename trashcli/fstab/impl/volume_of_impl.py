import os

from trashcli.fstab.is_mount import IsMount
from trashcli.fstab.volume_of import VolumeOf


class VolumeOfImpl(VolumeOf):
    def __init__(self,
                 ismount,  # type: IsMount
                 abspath,
                 ):
        self.ismount = ismount
        self.abspath = abspath

    def volume_of(self,
                  path,  # type: str
                  ):  # type: (...) -> str
        path = self.abspath(path)
        while path != os.path.dirname(path):
            if self.ismount.is_mount(path):
                break
            path = os.path.dirname(path)
        return path
