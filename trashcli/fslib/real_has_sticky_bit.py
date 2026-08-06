from trashcli.fslib.has_sticky_bit import HasStickyBit
from trashcli.fslib.real_read_sticky_bit_fs import RealReadStickyBitFs


class RealHasStickyBit(HasStickyBit):
    def has_sticky_bit(self, path):
        return RealReadStickyBitFs().is_sticky(path)
