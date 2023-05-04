import os
from abc import ABCMeta, abstractmethod

import six

from trashcli.fstab.volume_listing import RealIsMount


@six.add_metaclass(ABCMeta)
class VolumeOf:
    @abstractmethod
    def volume_of(self, path):
        raise NotImplementedError()


class RealVolumeOf(VolumeOf):
    def __init__(self):
        self.impl = VolumeOfImpl(RealIsMount(), os.path.abspath)

    def volume_of(self, path):
        return self.impl.volume_of(path)


class VolumeOfImpl(VolumeOf):
    def __init__(self, ismount, abspath):
        self.ismount = ismount
        self.abspath = abspath

    def volume_of(self, path):
        path = self.abspath(path)
        while path != os.path.dirname(path):
            if self.ismount.is_mount(path):
                break
            path = os.path.dirname(path)
        return path
