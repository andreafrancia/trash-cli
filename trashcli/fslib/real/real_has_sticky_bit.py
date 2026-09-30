import os
import stat

from trashcli.fslib.protocols.has_sticky_bit import HasStickyBit


class RealHasStickyBit(HasStickyBit):
    def has_sticky_bit(self, path):
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX
