import os

from trashcli.trash import DirReader


class MockDirReader(DirReader):
    def __init__(self):
        self.root = {}

    def entries_if_dir_exists(self, path):  # type: (str) -> list[str]
        return list(self.pick_dir(path).keys())

    def exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()

    def add_file(self, path):
        dirname, basename = os.path.split(path)
        dir = self.pick_dir(dirname)
        dir[basename] = ''

    def mkdir(self, path):
        dirname, basename = os.path.split(path)
        cwd = self.pick_dir(dirname)
        cwd[basename] = {}

    def pick_dir(self, dir):
        cwd = self.root
        components = dir.split('/')[1:]
        if components != ['']:
            for p in components:
                if p not in cwd:
                    raise FileNotFoundError("no such file or directory: %s" % dir)
                cwd = cwd[p]
        return cwd
