import os

from trashcli.fslib.is_sticky_dir import IsStickyDir
from trashcli.fslib.real_read_sticky_bit_fs import RealReadStickyBitFs


class RealIsStickyDir(IsStickyDir, RealReadStickyBitFs):
    def is_sticky_dir(self, path):  # type: (str) -> bool
        return os.path.isdir(path) and self.is_sticky(path)
