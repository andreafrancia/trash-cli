from typing import Callable, Mapping, List

from trashcli.fslib.force_remover import ForceRemover
from trashcli.fslib.remove_file_if_exists import RemoveFileIfExists
from trashcli.fslib.protocols.fs import Fs

class RmFsImpl:
    def __init__(self,
                 fs,  # type: Fs
                 environ,  # type: Mapping[str, str]
                 geteuid,  # type: Callable[[], int]
                 ):  # type: (...) -> None
        force_remover = ForceRemover(fs, environ, geteuid)
        fs_remove_file_if_exists = RemoveFileIfExists(fs, environ, geteuid)

        self.read_file = fs.read_file
        self.listdir = fs.listdir
        self.is_symlink = fs.is_symlink
        self.is_sticky_dir = fs.is_sticky_dir
        self.is_world_writable = fs.is_world_writable
        self.path_exists = fs.path_exists
        self.path_isdir = fs.path_isdir
        self.remove_path_forcefully = force_remover.remove_path_forcefully
        self.remove_file_if_exists = fs_remove_file_if_exists.remove_file_if_exists
