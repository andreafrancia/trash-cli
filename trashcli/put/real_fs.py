import os
import stat

from trashcli import fs
from trashcli.fs import write_file
from trashcli.put.fs import Fs


class DirScanner:
    def fallback_scandir(self, path):
        for path, dirs, files in os.walk(path):
            for f in files:
                yield os.path.join(path, f)


class RealFs(Fs):

    @staticmethod
    def atomic_write(path, content):
        fs.atomic_write(path, content)

    @staticmethod
    def chmod(path, mode):
        os.chmod(path, mode)

    @staticmethod
    def isdir(path):
        return os.path.isdir(path)

    @staticmethod
    def isfile(path):
        return os.path.isfile(path)

    def getsize(self, path):
        return os.path.getsize(path)

    def get_size_recursive(self, path):
        if os.path.isfile(path):
            return os.path.getsize(path)

        size = 0
        for f in self.scandir(path):
            size += os.path.getsize(f)

        return size

    def scandir(self, path):
        for f in DirScanner().fallback_scandir(path):
            yield f

    @staticmethod
    def exists(path):
        return os.path.exists(path)

    @staticmethod
    def makedirs(path, mode):
        os.makedirs(path, mode)

    @staticmethod
    def move(path, dest):
        return fs.move(path, dest)

    @staticmethod
    def remove_file(path):
        fs.remove_file(path)

    @staticmethod
    def islink(path):
        return os.path.islink(path)

    @staticmethod
    def has_sticky_bit(path):
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

    @staticmethod
    def realpath(path):
        return os.path.realpath(path)

    @staticmethod
    def is_accessible(path):
        return os.access(path, os.F_OK)

    @staticmethod
    def make_file(path, content):
        write_file(path, content)

    def get_mod(self, path):
        return stat.S_IMODE(os.lstat(path).st_mode)
