import shutil

from trashcli.fslib.protocols.move import ShutilMove


class RealShUtilMove(ShutilMove):
    def shutil_move(self, src, dst):  # type: (str, str) -> None
        shutil.move(src, str(dst))
