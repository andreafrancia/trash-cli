"""
Tests command to set and read sticky bits on directories.
"""
import os
import subprocess

from tests.support.dirs.my_path import MyPath


class OsCmds:
    @staticmethod
    def make_it_sticky(path):
        subprocess.check_call(["chmod", "1777", path])
    @staticmethod
    def make_it_not_sticky(path):
        subprocess.check_call(["chmod", "0777", path])
    @staticmethod
    def read_stickiness_from_ls_ld_output(path):
        ret = subprocess.check_output(["ls", "-ld", path])
        return ret.decode("ascii")[9]


class TestStickyBit:
    def setup_method(self):
        tmp = MyPath.make_temp_dir()
        self.dir_path = tmp / "foo"
        # make dir
        os.makedirs(self.dir_path, exist_ok=True)

    def test_how_to_set_with_real_os_commands_when_it_is_sticky(self):
        OsCmds.make_it_sticky(self.dir_path)

        char = OsCmds.read_stickiness_from_ls_ld_output(self.dir_path)

        assert char == 't'

    def test_how_to_set_with_real_os_commands_when_it_is_not_sticky(self):
        OsCmds.make_it_not_sticky(self.dir_path)

        char = OsCmds.read_stickiness_from_ls_ld_output(self.dir_path)

        assert char == 'x'

    def test_how_to_read_stickiness_with_python_when_is_sticky(self):
        OsCmds.make_it_sticky(self.dir_path)
        # read stickiness
        stickiness = self.is_sticky(self.dir_path)
        # should be sticky -> True
        assert stickiness == True

    def test_how_to_read_stickiness_with_python_when_is_not_sticky(self):
        OsCmds.make_it_not_sticky(self.dir_path)

        is_sticky = self.is_sticky(self.dir_path)

        assert is_sticky == False

    def is_sticky(self, path):
        return ReadStickyBitFs().is_sticky(path)

class ReadStickyBitFs:
    def is_sticky(self, path):
        import os
        import stat
        # get all the stats
        stat_result = os.stat(path) # type: os.stat_result
        # pick file mode (file type and file mode bits (permissions))
        # see https://docs.python.org/3/library/os.html
        mode = stat_result.st_mode
        # extract stickiness
        sticky_bit = mode & stat.S_ISVTX # type: int
        return sticky_bit == stat.S_ISVTX
