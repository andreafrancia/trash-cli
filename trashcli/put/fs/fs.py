from abc import abstractmethod
from typing import Protocol


class Fs(Protocol):

    @abstractmethod
    def atomic_write(self, path, content):
        pass

    @abstractmethod
    def chmod(self, path, mode):
        pass

    @abstractmethod
    def isdir(self, path):
        pass

    @abstractmethod
    def isfile(self, path):
        pass

    @abstractmethod
    def getsize(self, path):
        pass

    @abstractmethod
    def exists(self, path):
        pass

    @abstractmethod
    def makedirs(self, path, mode):
        pass

    @abstractmethod
    def move(self, path, dest):
        pass

    @abstractmethod
    def remove_file(self, path):
        pass

    @abstractmethod
    def islink(self, path):
        pass

    @abstractmethod
    def has_sticky_bit(self, path):
        pass

    @abstractmethod
    def realpath(self, path):
        pass

    @abstractmethod
    def is_accessible(self, path):
        pass

    @abstractmethod
    def make_file(self, path, content):
        pass

    @abstractmethod
    def get_mod(self, path):
        pass

    @abstractmethod
    def lexists(self, path):
        pass

    @abstractmethod
    def walk_no_follow(self, top):
        pass
