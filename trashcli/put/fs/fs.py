import os
from abc import abstractmethod
from trashcli.compat import Protocol


class RealPathFs(Protocol):
    @abstractmethod
    def realpath(self, path):
        raise NotImplementedError


class Fs(RealPathFs, Protocol):
    @abstractmethod
    def atomic_write(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def chmod(self, path, mode):
        raise NotImplementedError

    @abstractmethod
    def isdir(self, path):
        raise NotImplementedError

    @abstractmethod
    def isfile(self, path):
        raise NotImplementedError

    @abstractmethod
    def getsize(self, path):
        raise NotImplementedError

    @abstractmethod
    def exists(self, path):
        raise NotImplementedError

    @abstractmethod
    def makedirs(self, path, mode):
        raise NotImplementedError

    @abstractmethod
    def move(self, path, dest):
        raise NotImplementedError

    @abstractmethod
    def remove_file(self, path):
        raise NotImplementedError

    @abstractmethod
    def islink(self, path):
        raise NotImplementedError

    @abstractmethod
    def has_sticky_bit(self, path):
        raise NotImplementedError

    @abstractmethod
    def is_accessible(self, path):
        raise NotImplementedError

    @abstractmethod
    def make_file(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def get_mod(self, path):
        raise NotImplementedError

    @abstractmethod
    def lexists(self, path):
        raise NotImplementedError

    @abstractmethod
    def walk_no_follow(self, top):
        raise NotImplementedError

    def parent_realpath2(self, path):
        parent = os.path.dirname(path)
        return self.realpath(parent)
