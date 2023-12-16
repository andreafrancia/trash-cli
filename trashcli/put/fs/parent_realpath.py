import os

from trashcli.put.fs.fs import RealPathFs


class ParentRealpathFs:
    def __init__(self, fs):  # type: (RealPathFs) -> None
        self.fs = fs

    def parent_realpath(self, path):
        parent = os.path.dirname(path)
        return self.fs.realpath(parent)
