import stat
import os


class RealSetStickyBitFs:
    def set_sticky_bit(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

    def unset_sticky_bit(self, path):
        os.chmod(path, os.stat(path).st_mode & ~ stat.S_ISVTX)
