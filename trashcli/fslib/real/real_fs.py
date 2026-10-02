import os
import shutil
import stat
from typing import Iterable

from trashcli.fslib.real.real_is_world_writable import RealIsWorldWritable
from trashcli.fslib.real.real_list_files_in_dir import RealListFilesInDir
from trashcli.fslib.real.real_move import RealMove
from trashcli.fslib.real.real_remove_file import RealRemoveFile
from trashcli.fslib.real.real_atomic_write import RealAtomicWrite
from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.fslib.real.real_write_file import RealWriteFile
from trashcli.fslib.real.real_mk_dirs import RealMkDirs
from trashcli.fstab.mount_points_listing import RealMountPointListFs
from trashcli.fstab.real_volume_of import RealVolumeOf
from trashcli.fslib.protocols.fs import Fs
from trashcli.restore.fs.protocols.restore_fs import RestoreFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_read_cwd_fs import RealReadCwdFs
from trashcli.trash_dirs_scanner import TopTrashDirRulesFs


class RealFs(RealVolumeOf, Fs, RestoreFs, TopTrashDirRulesFs):

    def __init__(self):
        super(RealFs, self).__init__()

    def readlink(self, path):
        return os.readlink(path)

    def symlink(self, src, dest):  # type: (str, str) -> None
        os.symlink(src, dest)

    def touch(self, path):  # type: (str) -> None
        with open(path, 'a'):
            import os
            os.utime(path, None)

    def atomic_write(self, path, content):
        RealAtomicWrite().atomic_write(path, content)

    def chmod(self, path, mode):
        os.chmod(path, mode)

    def isfile(self, path):
        return os.path.isfile(path)

    def file_size(self, path):
        return os.path.getsize(path)

    def walk_no_follow(self, path):
        try:
            import scandir  # type: ignore
            walk = scandir.walk
        except ImportError:
            walk = os.walk

        return walk(path, followlinks=False)

    def makedirs(self, path, mode):
        os.makedirs(path, mode)

    def mkdir(self, path):
        os.mkdir(path)

    def mkdirs(self, path):
        RealMkDirs().mkdirs(path)

    def mkdir_with_mode(self, path, mode):
        os.mkdir(path, mode)

    def move(self, path, dest):
        return RealMove().move(path, dest)

    def remove_file(self, path):
        RealRemoveFile().remove_file(path)

    def remove(self, path):  # type: (str) -> None
        os.remove(path)

    def shutil_rmtree(self, path):  # type: (str) -> None
        shutil.rmtree(path)

    def is_symlink(self, path):
        return os.path.islink(path)

    def has_sticky_bit(self, path):
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

    def is_sticky_dir(self, path):  # type: (str) -> bool
        return os.path.isdir(path) and self.has_sticky_bit(path)

    def is_world_writable(self, path):  # type: (str) -> bool
        return RealIsWorldWritable().is_world_writable(path)

    def realpath(self, path):
        return os.path.realpath(path)

    def is_accessible(self, path):
        return os.access(path, os.F_OK)

    def seems_to_have_delete_permissions(self, path):
        # a file can be deleted only if its parent directory allows writing and searching
        parent = os.path.realpath(os.path.dirname(path) or os.curdir)
        return os.access(parent, os.W_OK | os.X_OK)

    def get_mod(self, path):
        return stat.S_IMODE(os.lstat(path).st_mode)

    def listdir(self, path):
        return os.listdir(path)

    def read_file(self, path):
        return RealReadFile().read_file(path)

    def write_file(self, path, content):
        return RealWriteFile().write_file(path, content)

    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        return RealListFilesInDir().list_files_in_dir(path)

    def path_exists(self, path):  # type: (str) -> bool
        return RealPathReaderFs().path_exists(path)

    def path_lexists(self, path):  # type: (str) -> bool
        return RealPathReaderFs().path_lexists(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return RealPathReaderFs().path_isdir(path)

    def getcwd_as_realpath(self):  # type: () -> str
        return RealReadCwdFs().getcwd_as_realpath()

    def list_mount_points(self):
        return RealMountPointListFs().list_mount_points()
