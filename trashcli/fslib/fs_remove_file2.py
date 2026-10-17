import errno
import os
import stat

from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.remove_file2 import RemoveFile2


class FsRemoveFile2(RemoveFile2):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_file2(self, path):
        try:
            self.fs.remove(path)
        except OSError:
            try:
                self.fs.shutil_rmtree(path)
            except OSError as e:
                # a missing write or search bit fails with EACCES
                if e.errno != errno.EACCES:
                    raise
                old_modes = []  # type: list
                self.add_write_permission(path, old_modes)
                # retry only if some directory got the missing bits
                if not old_modes:
                    raise
                try:
                    self.fs.shutil_rmtree(path)
                except OSError:
                    self.restore_modes(old_modes)
                    raise

    def add_write_permission(self, path, old_modes):  # type: (str, list) -> None
        """Add the owner write and search bits to path and to every dir under it."""
        if not self.fs.path_isdir(path) or self.fs.is_symlink(path):
            return
        mode = self.fs.get_mod(path)
        new_mode = mode | stat.S_IWUSR | stat.S_IXUSR
        if new_mode != mode:
            try:
                self.fs.chmod(path, new_mode)
            except OSError:
                # only the owner can change the mode
                return
            old_modes.append((path, mode))
        try:
            names = self.fs.listdir(path)
        except OSError:
            # an unreadable dir cannot be listed, its content is left as it is
            return
        # top down: a dir gets its search bit before its entries are visited
        for name in names:
            self.add_write_permission(os.path.join(path, name), old_modes)

    def restore_modes(self, old_modes):  # type: (list) -> None
        """Set back the old mode of each changed dir that is left."""
        # bottom up: a dir keeps its search bit until the dirs under it are restored
        for path, mode in reversed(old_modes):
            try:
                self.fs.chmod(path, mode)
            except OSError:
                # the dir was already removed
                pass
