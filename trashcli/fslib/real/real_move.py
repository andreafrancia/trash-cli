import errno
import os
import shutil
import stat
import tempfile

from trashcli.fslib.protocols.move import Move
from trashcli.fslib.protocols.move import PartlyMoved


class RealMove(Move):
    def move(self, path, dest):
        dest = str(dest)
        if not os.path.isdir(path) or os.path.islink(path):
            return shutil.move(path, dest)
        try:
            return os.rename(path, dest)
        except OSError as e:
            if e.errno != errno.EXDEV:
                # only an empty dir can be copied, it is removed in one step
                if os.listdir(path):
                    raise
                return shutil.move(path, dest)
        if os.path.realpath(dest).startswith(os.path.join(os.path.realpath(path), '')):
            raise OSError(errno.EINVAL, 'Cannot move a directory into itself', path)
        # the cleanup below must only remove a copy made here
        if os.path.lexists(dest):
            raise OSError(errno.EEXIST, 'File exists', dest)
        try:
            shutil.copytree(path, dest, symlinks=True)
            remove_step_by_step(path, dest)
        except PartlyMoved:
            raise
        except EnvironmentError as e:
            # the original is complete, so the copy is not needed, unless the copy never started
            if not (e.errno == errno.EEXIST and e.filename == dest):
                remove_copy(dest)
            raise


def remove_step_by_step(top, copy):  # type: (str, str) -> None
    # entries go to a holder on the same file system first, so every step can be undone
    holder = tempfile.mkdtemp(prefix='.trash-cli-',
                              dir=os.path.dirname(os.path.abspath(top)))
    done = []  # type: list
    try:
        for path in entries_bottom_up(top):
            copied = os.path.join(copy, os.path.relpath(path, top))
            if not is_copied(path, copied):
                raise OSError(errno.EAGAIN, 'Changed while moving', path)
            if os.path.isdir(path) and not os.path.islink(path):
                # rmdir needs no write permission on the dir and fails if it is not empty
                mode = stat.S_IMODE(os.lstat(path).st_mode)
                os.rmdir(path)
                done.append((path, mode))
            else:
                kept = os.path.join(holder, str(len(done)))
                os.rename(path, kept)
                done.append((path, kept))
    except OSError:
        put_back(done, holder)
        raise
    try:
        shutil.rmtree(holder)
    except OSError:
        # the copy is complete, the holder only keeps duplicates
        pass


def entries_bottom_up(top):  # type: (str) -> list
    entries = []  # type: list
    for root, dirs, files in os.walk(top, topdown=False):
        entries.extend(os.path.join(root, name) for name in files + dirs)
    return entries + [top]


def is_copied(path, copied):  # type: (str, str) -> bool
    # an entry added or changed during the copy is not in the copy as it is now
    try:
        a, b = os.lstat(path), os.lstat(copied)
    except OSError:
        return False
    if stat.S_IFMT(a.st_mode) != stat.S_IFMT(b.st_mode):
        return False
    return not stat.S_ISREG(a.st_mode) or a.st_size == b.st_size


def put_back(done, holder):  # type: (list, str) -> None
    failed = False
    for path, kept in reversed(done):
        # never replace what another program created there meanwhile
        if os.path.lexists(path):
            failed = True
            continue
        try:
            if isinstance(kept, int):
                os.mkdir(path, kept)
            else:
                os.rename(kept, path)
        except OSError:
            failed = True
    if failed:
        # the copy is complete and what could not be put back is in the holder
        raise PartlyMoved(errno.EIO, 'Partly moved, the rest is in %s' % holder, holder)
    os.rmdir(holder)


def remove_copy(copy):  # type: (str) -> None
    if not os.path.lexists(copy):
        return
    # the copy keeps the original modes, so its dirs are made writable first
    for root, dirs, files in os.walk(copy):
        os.chmod(root, 0o700)
    shutil.rmtree(copy)
