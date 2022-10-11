import os
import stat

from trashcli import fs


class RealFs:

    @staticmethod
    def atomic_write(path, content):
        fs.atomic_write(path, content)

    def ensure_dir(self, path, mode):
        if self.isdir(path):
            self.chmod(path, mode)
            return
        self.makedirs(path, mode)

    @staticmethod
    def chmod(path, mode):
        os.chmod(path, mode)

    @staticmethod
    def isdir(path):
        return os.path.isdir(path)

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
    def isdir(path):
        return os.path.isdir(path)

    @staticmethod
    def islink(path):
        return os.path.islink(path)

    @staticmethod
    def has_sticky_bit(path):
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX
