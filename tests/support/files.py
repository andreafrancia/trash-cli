import os
import shutil

from trashcli.fs import write_file, has_sticky_bit, mkdirs


def make_empty_file(path):
    make_file(path, '')


def make_file(filename, contents=''):
    make_parent_for(filename)
    write_file(filename, contents)


def require_empty_dir(path):
    if os.path.exists(path): shutil.rmtree(path)
    make_dirs(path)
    assert os.path.isdir(path)
    assert [] == list(os.listdir(path))


def make_dirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    assert os.path.isdir(path)


def make_parent_for(path):
    parent = os.path.dirname(os.path.realpath(path))
    make_dirs(parent)


def make_sticky_dir(path):
    os.mkdir(path)
    set_sticky_bit(path)


def make_unsticky_dir(path):
    os.mkdir(path)
    unset_sticky_bit(path)


def make_dir_unsticky(path):
    assert_is_dir(path)
    unset_sticky_bit(path)


def assert_is_dir(path):
    assert os.path.isdir(path)


def set_sticky_bit(path):
    import stat
    os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)


def unset_sticky_bit(path):
    import stat
    os.chmod(path, os.stat(path).st_mode & ~ stat.S_ISVTX)


def ensure_non_sticky_dir(path):
    import os
    assert os.path.isdir(path)
    assert not has_sticky_bit(path)


def make_unreadable_file(path):
    make_file(path, '')
    import os
    os.chmod(path, 0)


def make_unreadable_dir(path):
    mkdirs(path)
    os.chmod(path, 0o300)


def make_readable(path):
    os.chmod(path, 0o700)


def assert_dir_empty(path):
    assert len(os.listdir(path)) == 0


def assert_dir_contains(path, filename):
    assert os.path.exists(os.path.join(path, filename))
