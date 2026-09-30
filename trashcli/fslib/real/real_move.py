import shutil

from trashcli.fslib.protocols.move import Move


class RealMove(Move):
    def move(self, path, dest):
        return shutil.move(path, str(dest))
