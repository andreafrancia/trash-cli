import os
from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol
from trashcli.fslib.protocols.mk_dirs import MkDirs
from trashcli.fslib.protocols.real_path_fs import RealPathFs
from trashcli.fslib.protocols.volume_of import VolumeOfFs


class Fs(RealPathFs, VolumeOfFs, MkDirs, Protocol):
    @abstractmethod
    def touch(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def symlink(self, src, dest):  # type: (str, str) -> None
        raise NotImplementedError

    @abstractmethod
    def mkdir(self, path):  # type: (str) -> None
        raise NotImplementedError

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
    def remove(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def shutil_rmtree(self, path):  # type: (str) -> None
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
    def read_file(self, path):
        raise NotImplementedError

    @abstractmethod
    def write_file(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def get_mod(self, path):
        raise NotImplementedError

    @abstractmethod
    def path_lexists(self, path):
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError

    @abstractmethod
    def walk_no_follow(self, top):
        raise NotImplementedError

    def parent_realpath2(self, path):
        parent = os.path.dirname(path)
        return self.realpath(parent)

    def list_sorted(self, path):
        return sorted(self.listdir(path))
