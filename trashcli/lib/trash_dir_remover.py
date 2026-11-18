import errno
import os
from typing import Optional

from trashcli.fslib.fs_remove_file2 import FsRemoveFile2
from trashcli.fslib.protocols.fs import Fs
from trashcli.lib.trash_dirs import is_trash_dir_of, is_volume_trash_dir


class TrashDirRemover:
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def check_trash_dir(self, trash_dir, volume, uid=None):
        # type: (str, str, Optional[int]) -> os.stat_result
        """Return the stat of trash_dir after checking it is a dir of its user."""
        if is_volume_trash_dir(trash_dir, volume):
            # other users may be able to put a symlink at this name
            found = self.fs.lstat(os.path.normpath(trash_dir))
        else:
            found = self.fs.stat(trash_dir)
        if not is_trash_dir_of(found, uid, self.fs.geteuid()):
            raise OSError(errno.EPERM, 'Not a trash dir of this user', trash_dir)
        return found

    def remove_if_exists(self, checked_dir, path):  # type: (os.stat_result, str) -> None
        """Remove path from inside its dir, which must sit directly in checked_dir."""
        if not self.fs.path_lexists(path):
            return
        try:
            start = self.fs.getcwd_as_realpath()
        except OSError:
            # the start dir is gone, absolute paths still work
            start = None
        # once inside, renaming a dir on the way cannot move the removal elsewhere
        self.fs.chdir(os.path.dirname(path))
        try:
            if not same_file(self.fs.stat('..'), checked_dir):
                raise OSError(errno.EPERM, 'Not inside the checked trash dir', path)
            FsRemoveFile2(self.fs).remove_file2(os.path.basename(path))
        finally:
            if start is not None:
                try:
                    self.fs.chdir(start)
                except OSError:
                    # the start dir can be gone, removed with the trash
                    pass


def same_file(a, b):  # type: (os.stat_result, os.stat_result) -> bool
    return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
