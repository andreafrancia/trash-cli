import os

from trashcli.fslib.protocols.listdir_fs import ListdirFs


class RealListdirFs(ListdirFs):
    def listdir(self, path):
        return os.listdir(path)
