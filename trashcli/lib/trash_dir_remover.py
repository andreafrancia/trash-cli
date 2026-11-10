import errno
import os
import stat


def remove_in_trash_dir(trash_dir, path):  # type: (str, str) -> None
    """Remove path from inside its dir, after checking that dir is directly in trash_dir."""
    trash_dir, path = os.path.abspath(trash_dir), os.path.abspath(path)
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = None
    # once inside, renaming a dir on the way cannot move the removal elsewhere
    os.chdir(os.path.dirname(path))
    try:
        check_inside(trash_dir)
        remove_entry(os.path.basename(path))
    finally:
        if cwd is not None:
            os.chdir(cwd)


def check_inside(trash_dir):  # type: (str) -> None
    named = os.lstat(trash_dir)
    # a symlink to the trash dir is followed only if this user or root made it
    if stat.S_ISLNK(named.st_mode) and named.st_uid in (os.geteuid(), 0):
        named = os.stat(trash_dir)
    # the dir entered must sit directly in the trash dir as it is named now
    if not stat.S_ISDIR(named.st_mode) or not same_file(named, os.stat('..')):
        raise OSError(errno.EPERM, 'Not inside the trash dir', trash_dir)
    # only root may empty the trash dir of another user
    if os.geteuid() not in (0, named.st_uid) or os.stat('.').st_uid != named.st_uid:
        raise OSError(errno.EPERM, 'Trash dir of another user', trash_dir)


def remove_entry(name):  # type: (str) -> None
    entry = os.lstat(name)
    if not stat.S_ISDIR(entry.st_mode):
        os.unlink(name)
        return
    parent = os.stat('.')
    os.chdir(name)
    try:
        # the dir entered must be the one just checked, not a symlink swapped in
        if not same_file(os.stat('.'), entry):
            raise OSError(errno.EAGAIN, 'Changed while removing', name)
        for child in os.listdir('.'):
            remove_entry(child)
    finally:
        os.chdir('..')
        # stop if the dir was moved meanwhile and '..' is now another dir
        if not same_file(os.stat('.'), parent):
            raise OSError(errno.EAGAIN, 'Changed while removing', name)
    os.rmdir(name)


def same_file(a, b):  # type: (os.stat_result, os.stat_result) -> bool
    return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
