import os

from trashcli import fs


class RestoreFileSystem:
    def __init__(self, default_cur_dir=None):
        self.default_cur_dir = default_cur_dir

    def path_exists(self, path):
        return os.path.exists(path)

    def mkdirs(self, path):
        return fs.mkdirs(path)

    def move(self, path, dest):
        return fs.move(path, dest)

    def remove_file(self, path):
        return fs.remove_file(path)

    def getcwd_as_realpath(self):
        if type(self.default_cur_dir) == str:
            return self.default_cur_dir
        if self.default_cur_dir:
            return self.default_cur_dir()
        return os.path.realpath(os.curdir)


class FakeRestoreFileSystem(RestoreFileSystem):
    def __init__(self, default_cur_dir=None):
        self.default_cur_dir = default_cur_dir

    def chdir(self, path):
        self.default_cur_dir = path

    def getcwd_as_realpath(self):
        return self.default_cur_dir


def getcwd_as_realpath():
    return os.path.realpath(os.curdir)
