from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.real.real_entries_if_dir_exists import \
    RealEntriesIfDirExists
from trashcli.list.list_fs import ListFs


class ListFsImpl(ListFs):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def entries_if_dir_exists(self, path):
        return RealEntriesIfDirExists(self.fs).entries_if_dir_exists(path)

    def path_exists(self, path):  # type: (str) -> bool
        return self.fs.path_exists(path)

    def is_sticky_dir(self, path):  # type: (str) -> bool
        return self.fs.is_sticky_dir(path)

    def has_sticky_bit(self, path):  # type: (str) -> bool
        return self.fs.has_sticky_bit(path)

    def is_symlink(self, path):  # type: (str) -> bool
        return self.fs.is_symlink(path)

    def read_file(self, path):  # type: (str) -> str
        return self.fs.read_file(path)

    def file_size(self, path):  # type: (str) -> int
        return self.fs.file_size(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return self.fs.path_isdir(path)

    def is_world_writable(self, path):  # type: (str) -> bool
        return self.fs.is_world_writable(path)
