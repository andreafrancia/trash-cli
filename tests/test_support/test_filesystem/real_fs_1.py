import os

from trashcli.fslib.real_fs_operations import RealMkDirs, \
    RealWriteFile
from trashcli.fslib.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real_has_sticky_bit import RealHasStickyBit
from trashcli.fslib.real_read_sticky_bit_fs import RealReadStickyBitFs
from trashcli.fslib.real_set_sticky_bit_fs import RealSetStickyBitFs


class RealFs1:
    def has_sticky_bit(self, path):
        return RealReadStickyBitFs().is_sticky(path)

    def mkdirs(self, path):
        RealMkDirs().mkdirs(path)

    def make_file(self, filename, contents=''):
        self.make_parent_for(filename)
        self.write_file(filename, contents)

    def make_parent_for(self, path):
        parent = os.path.dirname(os.path.realpath(path))
        self.make_dirs(parent)

    def write_file(self, filename, contents):
        RealWriteFile().write_file(filename, contents)

    def make_dirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        assert os.path.isdir(path)

    set_sticky_bit = RealSetStickyBitFs().set_sticky_bit
    unset_sticky_bit = RealSetStickyBitFs().unset_sticky_bit

    def make_empty_file(self, path):
        self.make_file(path, '')


    def is_sticky_dir(self, path):
        return RealIsStickyDir().is_sticky_dir(path)
