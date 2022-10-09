import os


class ParentRealpath:
    def __init__(self, realpath):
        self.realpath = realpath

    def parent_realpath(self, path):
        parent = os.path.dirname(path)
        return self.realpath(parent)
