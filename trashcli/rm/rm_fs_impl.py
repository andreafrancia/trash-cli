from typing import Callable, Mapping

from trashcli.fslib.real.real_entries_if_dir_exists import \
    RealEntriesIfDirExists
from trashcli.fslib.fs_remove_file2 import FsRemoveFile2
from trashcli.fslib.fs_remove_file_if_exists import FsRemoveFileIfExists
from trashcli.fslib.protocols.fs import Fs
from trashcli.rm.rm_cmd import RmFs

class RmFsImpl(RmFs):
    def __init__(self,
                 fs,  # type: Fs
                 environ,  # type: Mapping[str, str]
                 geteuid,  # type: Callable[[], int]
                 ):  # type: (...) -> None
        self.fs = fs
        self.environ = environ
        self.geteuid = geteuid

    def read_file(self, path):
        return self.fs.read_file(path)

    def is_symlink(self, path):  # type: (str) -> bool
        return self.fs.is_symlink(path)

    def is_sticky_dir(self, path):  # type: (str) -> bool
        return self.fs.is_sticky_dir(path)

    def is_world_writable(self, path):  # type: (str) -> bool
        return self.fs.is_world_writable(path)

    def entries_if_dir_exists(self, path):
        return RealEntriesIfDirExists(self.fs).entries_if_dir_exists(path)

    def path_exists(self, path):  # type: (str) -> bool
        return self.fs.path_exists(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return self.fs.path_isdir(path)

    def remove_file2(self, path):
        return FsRemoveFile2(self.fs, self.environ, self.geteuid).remove_file2(path)

    def remove_file_if_exists(self, path):
        return FsRemoveFileIfExists(self.fs, self.environ,
                                    self.geteuid).remove_file_if_exists(path)
