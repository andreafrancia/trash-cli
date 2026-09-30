import os

from trashcli.fslib.protocols.path_exists import PathExists


class RealExists(PathExists):
    def path_exists(self, path):  # type: (str) -> bool
        return os.path.exists(path)
