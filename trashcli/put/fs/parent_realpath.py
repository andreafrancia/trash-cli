import os


class ParentRealpathFs:
    def __init__(self, fs):
        self.fs = fs

    def parent_realpath(self, path):
        parent = os.path.dirname(path)
        return self.fs.realpath(parent)
