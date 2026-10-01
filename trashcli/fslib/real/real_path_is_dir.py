import os

from trashcli.fslib.protocols.path_is_dir import PathIsDir


class RealPathIsDir(PathIsDir):
    def path_isdir(self, path):  # type: (str) -> bool
        return os.path.isdir(path)
