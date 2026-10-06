import errno
import os

from trashcli.fslib.protocols.fs import Fs


class PartlyMoved(OSError):
    # the source could not be removed nor put back, so the copy is the only complete one
    def __init__(self, holder):  # type: (str) -> None
        super(PartlyMoved, self).__init__(
            errno.EIO, "partly moved, the removed entries are in %s" % holder)


def clean_move(fs, src, dest):  # type: (Fs, str, str) -> None
    # a move either completes or leaves the source as it was
    if not is_dir_with_content(fs, src):
        fs.move(src, dest)
    elif not renamed_unless_other_fs(fs, src, dest):
        copy_then_remove(fs, src, dest)


def is_dir_with_content(fs, path):  # type: (Fs, str) -> bool
    # files, symlinks and empty dirs are moved in a single step
    return (fs.path_isdir(path) and not fs.is_symlink(path) and
            len(fs.listdir(path)) > 0)


def renamed_unless_other_fs(fs, src, dest):  # type: (Fs, str, str) -> bool
    # on one file system a dir that cannot be renamed is never copied
    try:
        fs.rename(src, dest)
        return True
    except OSError as e:
        if e.errno != errno.EXDEV:
            raise
        return False


def copy_then_remove(fs, src, dest):  # type: (Fs, str, str) -> None
    try:
        fs.copytree(src, dest)
        remove_step_by_step(fs, src)
    except PartlyMoved:
        raise
    except EnvironmentError:
        # the source is complete, so the copy is not needed
        remove_copy(fs, dest)
        raise


def remove_step_by_step(fs, src):  # type: (Fs, str) -> None
    # each removed entry goes to a holder dir on the same file system, so every step can be undone
    holder = fs.mkdtemp('.trash-cli-', os.path.dirname(src) or os.curdir)
    done = []  # type: list
    try:
        for path in entries_bottom_up(fs, src):
            done.append(remove_entry(fs, path, holder, len(done)))
    except OSError:
        put_back(fs, done, holder)
        raise
    fs.shutil_rmtree(holder)


def entries_bottom_up(fs, top):  # type: (Fs, str) -> list
    # the content of a dir comes before the dir, the top dir comes last
    entries = []  # type: list
    for root, dirs, files in reversed(list(fs.walk_no_follow(top))):
        entries.extend(os.path.join(root, name) for name in files + dirs)
    return entries + [top]


def remove_entry(fs, path, holder, index):  # type: (Fs, str, str, int) -> tuple
    # a dir is already empty and is removed, any other entry is renamed into the holder
    if fs.path_isdir(path) and not fs.is_symlink(path):
        mode = fs.get_mod(path)
        fs.rmdir(path)
        return path, mode, None
    kept = os.path.join(holder, '%d-%s' % (index, os.path.basename(path)))
    fs.rename(path, kept)
    return path, None, kept


def put_back(fs, done, holder):  # type: (Fs, list, str) -> None
    # undo the done steps in reverse order, what cannot be put back stays in the holder
    failed = False
    for path, mode, kept in reversed(done):
        try:
            if kept is None:
                fs.mkdir(path)
                fs.chmod(path, mode)
            else:
                fs.rename(kept, path)
        except OSError:
            failed = True
    if failed:
        raise PartlyMoved(holder)
    fs.rmdir(holder)


def remove_copy(fs, copy):  # type: (Fs, str) -> None
    # the copy keeps the original modes, so its dirs are made writable first
    if not fs.path_lexists(copy):
        return
    for root, dirs, files in fs.walk_no_follow(copy):
        fs.chmod(root, 0o700)
    fs.remove_file(copy)
