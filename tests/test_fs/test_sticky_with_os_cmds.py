"""
Test that function for setting and reading sticky bit build around real
unix commands. These functions will be used as fixture for RealReadStickyBitFs
tests.
"""
import os

from tests.support.dirs.my_path import MyPath
from tests.test_fs.support.sticky_os import make_it_not_sticky_with_chmod
from tests.test_fs.support.sticky_os import make_it_sticky_with_chmod
from tests.test_fs.support.sticky_os import read_stickiness_from_ls_ld_output


class TestStickyBitWithOsCmds:
    def setup_method(self):
        # prepare a directory
        tmp = MyPath.make_temp_dir()
        self.dir_path = tmp / "foo"
        os.makedirs(self.dir_path, exist_ok=True)

    def test_how_to_set_with_real_os_commands_when_it_is_sticky(self):
        make_it_sticky_with_chmod(self.dir_path)

        char = read_stickiness_from_ls_ld_output(self.dir_path)

        assert char == 't'

    def test_how_to_set_with_real_os_commands_when_it_is_not_sticky(self):
        make_it_not_sticky_with_chmod(self.dir_path)

        char = read_stickiness_from_ls_ld_output(self.dir_path)

        assert char == 'x'

