import os
import stat

from trashcli.fslib.protocols.make_file_executable import MakeFileExecutable


class RealMakeFileExecutable(MakeFileExecutable):
    def make_file_executable(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
