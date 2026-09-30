import os
from abc import abstractmethod

from trashcli.compat import Protocol
from trashcli.fslib.protocols.real_path_fs import RealPathFs
from trashcli.fstab.volume_of import VolumeOf


class Fs(RealPathFs, VolumeOf, Protocol):
    @abstractmethod
    def atomic_write(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def chmod(self, path, mode):
        raise NotImplementedError

    @abstractmethod
    def path_isdir(self, path):
        raise NotImplementedError

    @abstractmethod
    def isfile(self, path):
        raise NotImplementedError

    @abstractmethod
    def file_size(self, path):
        raise NotImplementedError

    @abstractmethod
    def path_exists(self, path):
        raise NotImplementedError

    @abstractmethod
    def makedirs(self, path, mode):  # type: (str, int)->None
        raise NotImplementedError

    @abstractmethod
    def move(self, path, dest):
        raise NotImplementedError

    @abstractmethod
    def remove_file(self, path):
        raise NotImplementedError

    @abstractmethod
    def is_symlink(self, path):
        raise NotImplementedError

    @abstractmethod
    def has_sticky_bit(self, path):
        raise NotImplementedError

    @abstractmethod
    def is_accessible(self, path):
        raise NotImplementedError

    @abstractmethod
    def seems_to_have_delete_permissions(self, path):
        raise NotImplementedError

    @abstractmethod
    def read(self, path):
        raise NotImplementedError

    @abstractmethod
    def write_file(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def make_file(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def get_mod(self, path):
        raise NotImplementedError

    @abstractmethod
    def path_lexists(self, path):
        raise NotImplementedError

    @abstractmethod
    def walk_no_follow(self, top):
        raise NotImplementedError

    def parent_realpath2(self, path):
        parent = os.path.dirname(path)
        return self.realpath(parent)

    def list_sorted(self, path):
        return sorted(self.listdir(path))
