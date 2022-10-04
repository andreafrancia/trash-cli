import os
import stat

from trashcli import fs


class RealFs:

    def atomic_write(self, path, content):
        fs.atomic_write(path, content)

    @staticmethod
    def ensure_dir(path, mode):
        if os.path.isdir(path):
            os.chmod(path, mode)
            return
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
