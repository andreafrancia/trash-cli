import os

from trashcli.fslib.protocols.mk_dirs import MkDirs


class RealMkDirs(MkDirs):
    def mkdirs(self, path):
        if os.path.isdir(path):
            return
        os.makedirs(path)
