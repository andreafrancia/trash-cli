import os
import stat

from trashcli import fs
from trashcli.fs import write_file
from trashcli.put.fs.fs import Fs


class RealFs(Fs):

    def atomic_write(self, path, content):
        fs.atomic_write(path, content)

    def chmod(self, path, mode):
        os.chmod(path, mode)

    def isdir(self, path):
        return os.path.isdir(path)

    def isfile(self, path):
        return os.path.isfile(path)

    def getsize(self, path):
        return os.path.getsize(path)

    def walk_no_follow(self, path):
        try:
            import scandir  # type: ignore
            walk = scandir.walk
        except ImportError:
            walk = os.walk

        return walk(path, followlinks=False)

    def exists(self, path):
        return os.path.exists(path)

    def makedirs(self, path, mode):
        os.makedirs(path, mode)

    def move(self, path, dest):
        return fs.move(path, dest)

    def remove_file(self, path):
        fs.remove_file(path)

    def islink(self, path):
        return os.path.islink(path)

    def has_sticky_bit(self, path):
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

    def realpath(self, path):
        return os.path.realpath(path)

    def is_accessible(self, path):
        return os.access(path, os.F_OK)

    def make_file(self, path, content):
        write_file(path, content)

    def get_mod(self, path):
        return stat.S_IMODE(os.lstat(path).st_mode)

    def listdir(self, path):
        return os.listdir(path)

    def lexists(self, path):
        return os.path.lexists(path)
