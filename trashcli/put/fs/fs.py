import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Fs:

    @abc.abstractmethod
    def atomic_write(self, path, content):
        pass

    @abc.abstractmethod
    def chmod(self, path, mode):
        pass

    @abc.abstractmethod
    def isdir(self, path):
        pass

    @abc.abstractmethod
    def isfile(self, path):
        pass

    @abc.abstractmethod
    def getsize(self, path):
        pass

    @abc.abstractmethod
    def exists(self, path):
        pass

    @abc.abstractmethod
    def makedirs(self, path, mode):
        pass

    @abc.abstractmethod
    def move(self, path, dest):
        pass

    @abc.abstractmethod
    def remove_file(self, path):
        pass

    @abc.abstractmethod
    def islink(self, path):
        pass

    @abc.abstractmethod
    def has_sticky_bit(self, path):
        pass

    @abc.abstractmethod
    def realpath(self, path):
        pass

    @abc.abstractmethod
    def is_accessible(self, path):
        pass

    @abc.abstractmethod
    def make_file(self, path, content):
        pass

    @abc.abstractmethod
    def get_mod(self, path):
        pass

    @abc.abstractmethod
    def lexists(self, path):
        pass
