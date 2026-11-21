import shutil

from trashcli.fslib.protocols.move import Move


class RealMove(Move):
    def move(self, src, dst):  # type: (str, str) -> None
        shutil.move(src, str(dst))
