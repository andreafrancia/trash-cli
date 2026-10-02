import errno
import os
import shutil
import stat

from trashcli.fslib.protocols.remove_file2 import RemoveFile2


class RealRemoveFile2(RemoveFile2):
    def remove_file2(self, path):
        try:
            os.remove(path)
        except OSError:
            try:
                shutil.rmtree(path)
            except OSError as e:
                # a missing write or search bit fails with EACCES
                if e.errno != errno.EACCES:
                    raise
                old_modes = _add_write_permission(path)
                # retry only if some directory got the missing bits
                if not old_modes:
                    raise
                try:
                    shutil.rmtree(path)
                except OSError:
                    _restore_modes(path, old_modes)
                    raise


def _add_write_permission(path):
    # add owner write and search bits to own directories, return old modes
    old_modes = {}
    for fd in _dir_fds(path, topdown=True):
        try:
            st = os.fstat(fd)
            old = stat.S_IMODE(st.st_mode)
            new = old | stat.S_IWUSR | stat.S_IXUSR
            if new != old and st.st_uid == os.geteuid():
                os.fchmod(fd, new)
                old_modes[(st.st_dev, st.st_ino)] = old
        except OSError:
            pass
    return old_modes


def _restore_modes(path, old_modes):
    # set back the old mode of each changed directory that is left
    for fd in _dir_fds(path, topdown=False):
        try:
            st = os.fstat(fd)
            if (st.st_dev, st.st_ino) in old_modes:
                os.fchmod(fd, old_modes[(st.st_dev, st.st_ino)])
        except OSError:
            pass


def _dir_fds(path, topdown):
    # yield a handle for each directory under path, never follow symlinks
    if hasattr(os, 'fwalk'):
        try:
            for _, _, _, fd in os.fwalk(path, topdown=topdown,
                                        follow_symlinks=False):
                yield fd
        except OSError:
            pass
        return
    for root, _, _ in os.walk(path, topdown=topdown, followlinks=False):
        try:
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError:
            continue
        try:
            yield fd
        finally:
            os.close(fd)
