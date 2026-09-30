import os

from trashcli.fslib.protocols.is_sticky_dir import IsStickyDir
from trashcli.fslib.real.real_has_sticky_bit import RealHasStickyBit


class RealIsStickyDir(IsStickyDir, RealHasStickyBit):
    def is_sticky_dir(self, path):  # type: (str) -> bool
        return os.path.isdir(path) and self.has_sticky_bit(path)
