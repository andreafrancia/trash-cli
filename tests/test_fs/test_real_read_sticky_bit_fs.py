"""
Tests command to set and read sticky bits on directories.
"""
import os

from tests.support.dirs.my_path import MyPath
from tests.test_fs.real_read_sticky_bit_fs import RealReadStickyBitFs
from tests.support.fs_support.sticky_os import make_it_not_sticky_with_chmod
from tests.support.fs_support.sticky_os import make_it_sticky_with_chmod


class TestStickyBit:
    def setup_method(self):
        tmp = MyPath.make_temp_dir()
        self.dir_path = tmp / "bar"
        os.makedirs(self.dir_path, exist_ok=True)

    def test_when_it_is_sticky_it_returns_true(self):
        make_it_sticky_with_chmod(self.dir_path)

        stickiness = self.is_sticky(self.dir_path)

        assert stickiness == True

    def test_when_it_is_not_sticky_it_returns_false(self):
        make_it_not_sticky_with_chmod(self.dir_path)

        is_sticky = self.is_sticky(self.dir_path)

        assert is_sticky == False

    @staticmethod
    def is_sticky(path):
        return RealReadStickyBitFs().is_sticky(path)

