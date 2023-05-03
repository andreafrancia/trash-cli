import os
from abc import ABCMeta, abstractmethod

import six

from trashcli.fstab.is_mount import RealIsMount


@six.add_metaclass(ABCMeta)
class Volumes:
    @abstractmethod
    def volume_of(self, path):
        raise NotImplementedError()


class RealVolumes(Volumes):
    def __init__(self):
        self.impl = VolumesImpl(RealIsMount(), os.path.abspath)

    def volume_of(self, path):
        return self.impl.volume_of(path)


class VolumesImpl:
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
