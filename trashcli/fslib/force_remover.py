import errno
import os
import stat
from abc import abstractmethod
from typing import Callable, Mapping, List, NamedTuple

from trashcli.compat import Protocol
from trashcli.lib.trash_dirs import home_trash_dir_path_from_env


class ForceRemover:
    def __init__(self,
                 fs,  # type: ForceRemoveFs
                 environ,  # type: Mapping[str, str]
                 geteuid,  # type: Callable[[], int]
                 ):  # type: (...) -> None
        self.fs = fs
        self.environ = environ
        self.geteuid = geteuid

    def remove_path_forcefully(self, path):  # type: (str) -> None
        try:
            self.fs.remove(path)
        except OSError:
            try:
                self.fs.shutil_rmtree(path)
            except OSError as e:
                # root needs no help, and outside the home trash another user could redirect the chmod with a symlink
                if not self.should_self_heal(e,
                                             self.geteuid(),
                                             self.is_in_home_trash(path)):
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

    @staticmethod
    def should_self_heal(e,  # type: OSError
                         euid,  # type: int
                         in_home_trash,  # type: bool
                         ):  # type: (...) -> bool
        if euid == 0:
            # root needs no help
            return False
        if e.errno != errno.EACCES:
            # with permission changes we can heal only on EACCES
            return False
        if not in_home_trash:
            # outside the home trash another user could redirect the chmod with
            # a symlink
            return False

        # if it is a user that can remove files in the home trash for
        # permission problems, we will heal
        return True

    def add_write_permission(self,
                             path,  # type: str
                             old_modes,  # type: List[ModeToRestore]
                             ):  # type: (...) -> None
        """Add the owner write and search bits to path and to every dir under it."""
        if not self.fs.path_isdir(path) or self.fs.is_symlink(path):
            return
        mode = self.fs.get_mod(path)
        # owner bits only: a dir swapped for a symlink must not open its target to others
        new_mode = (mode | stat.S_IWUSR | stat.S_IXUSR) & stat.S_IRWXU
        if new_mode != mode & stat.S_IRWXU:
            try:
                self.fs.chmod(path, new_mode)
            except OSError:
                # only the owner can change the mode
                return
            old_modes.append(ModeToRestore(path, mode))
        try:
            names = self.fs.listdir(path)
        except OSError:
            # an unreadable dir cannot be listed, its content is left as it is
            return
        # top down: a dir gets its search bit before its entries are visited
        for name in names:
            self.add_write_permission(os.path.join(path, name), old_modes)

    def restore_modes(self,
                      old_modes,  # type: List[ModeToRestore]
                      ):  # type: (...) -> None
        """Set back the old mode of each changed dir that is left."""
        # bottom up: a dir keeps its search bit until the dirs under it are restored
        for path, mode in reversed(old_modes):
            try:
                # owner bits only, as when adding them: a swapped symlink must not open its target
                self.fs.chmod(path, keep_only_user_bits(mode))
            except OSError:
                # the dir was already removed
                pass

    def is_in_home_trash(self, path):  # type: (str) -> bool
        """True if path is in the home trash and that trash really is inside the home dir."""
        if 'HOME' not in self.environ:
            return False
        home = self.fs.realpath(self.environ['HOME']) + os.sep
        return any(path.startswith(trash + os.sep) and self.fs.realpath(
            trash).startswith(home)
                   for trash in home_trash_dir_path_from_env(self.environ))


def keep_only_user_bits(mode):  # type: (int) -> int
    return mode & stat.S_IRWXU


class ModeToRestore(NamedTuple('ModeToRestore', [
    ('path', str),
    ('mode', int)
])):
    pass


class ForceRemoveFs(Protocol):
    @abstractmethod
    def remove(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def shutil_rmtree(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def path_isdir(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def get_mod(self, path):  # type: (str) -> int
        raise NotImplementedError

    @abstractmethod
    def chmod(self, path, mode):  # type: (str, int) -> None
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError

    @abstractmethod
    def realpath(self, path):
        raise NotImplementedError
