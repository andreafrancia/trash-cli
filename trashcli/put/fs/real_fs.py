import grp
import os
import pwd
import shutil
import stat
from typing import NamedTuple
from typing import Optional

from trashcli.fs_impl import RealListFilesInDir

from trashcli.fs_impl import RealAtomicWrite
from trashcli.fs_impl import RealPathExists
from trashcli.fs_impl import RealFileSize
from trashcli.fs_impl import RealIsStickyDir
from trashcli.fs_impl import RealMakeFileExecutable
from trashcli.fs_impl import RealMkDirs
from trashcli.fs_impl import RealMove
from trashcli.fs_impl import RealFileReader
from trashcli.fs_impl import RealRemoveFile
from trashcli.fs_impl import RealRemoveFile2
from trashcli.fs_impl import RealWriteFile
from trashcli.fstab.real_volume_of import RealVolumeOf
from trashcli.lib import TrashInfoContent
from trashcli.put.fs.fs import Fs
from trashcli.put.fs.fs import ModeNotSpecified
from trashcli.put.fs.script_fs import ScriptFs


class Names:
    def username(self, uid):  # type: (int) -> Optional[str]
        try:
            return pwd.getpwuid(uid).pw_name
        except KeyError as e:
            return None

    def groupname(self, gid):
        try:
            return grp.getgrgid(gid).gr_name
        except KeyError as e:
            return None


class Stat(NamedTuple('Stat', [
    ('mode', int),
    ('uid', int),
    ('gid', int),
])):
    def is_executable(self):  # type: (...) -> bool
        return (self.mode & 0o500) == 0o500


class RealFs(RealVolumeOf, RealMkDirs, RealAtomicWrite,
             RealFileReader, RealWriteFile, RealFileSize,
             RealRemoveFile2, RealIsStickyDir,
             RealMakeFileExecutable, RealPathExists,
             RealRemoveFile, RealListFilesInDir,
             ScriptFs,
             Fs):

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

    def chmod(self, path, mode):
        os.chmod(path, mode)

    def isdir(self, path):
        return os.path.isdir(path)

    def isfile(self, path):
        return os.path.isfile(path)

    def get_file_size(self, path):
        return os.path.getsize(path)

    def walk_no_follow(self, path):
        try:
            import scandir  # type: ignore
            walk = scandir.walk
        except ImportError:
            walk = os.walk

        return walk(path, followlinks=False)

    def makedirs(self, path, mode=ModeNotSpecified):
        if mode is ModeNotSpecified:
            os.makedirs(path)
        else:
            os.makedirs(path, mode)

    def lstat(self, path):
        stat = os.lstat(path)
        return Stat(mode=stat.st_mode, uid=stat.st_uid, gid=stat.st_gid)

    def mkdir(self, path):
        os.mkdir(path)

    def mkdir_with_mode(self, path, mode):
        os.mkdir(path, mode)

    def move(self, path, dest):
        return RealMove().move(path, dest)

    def islink(self, path):
        return os.path.islink(path)

    def has_sticky_bit(self, path):
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

    def realpath(self, path):
        return os.path.realpath(path)

    def is_accessible(self, path):
        return os.access(path, os.F_OK)

    def make_file(self,
                  path,
                  content,  # type: TrashInfoContent
                  ):  # type: (...) -> None
        self.write_file(path, content)

    def get_mod(self, path):
        return stat.S_IMODE(os.lstat(path).st_mode)

    def listdir(self, path):
        return os.listdir(path)

    def lexists(self, path):
        return os.path.lexists(path)

    def set_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

    def unset_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode & ~ stat.S_ISVTX)

    def remove_dir_if_exists(self, dir):
        if os.path.exists(dir):
            os.rmdir(dir)

    def rmtree(self, path):
        shutil.rmtree(path)
