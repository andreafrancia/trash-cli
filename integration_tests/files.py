# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equal
from trashcli.fs  import has_sticky_bit
import os, shutil


def make_empty_file(path):
    write_file(path, '')


def write_file(filename, contents=''):
    parent = os.path.dirname(os.path.realpath(filename))
    if not os.path.isdir(parent): os.makedirs(parent)
    with open(filename, 'w') as f:
        f.write(contents)


def read_file(path):
    with open(path) as f:
        return f.read()


def require_empty_dir(path):
    if os.path.exists(path): shutil.rmtree(path)
    make_dirs(path)
    assert os.path.isdir(path)
    assert_equal([], list(os.listdir(path)))


def make_dirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    assert os.path.isdir(path)

def make_parent_for(path):
    parent = os.path.dirname(path)
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
    assert not has_sticky_bit(path)

def touch(path):
    open(path,'a+').close()

def ensure_non_sticky_dir(path):
    import os
    assert os.path.isdir(path)
    assert not has_sticky_bit(path)

def make_unreadable_file(path):
    write_file(path, '')
    import os
    os.chmod(path, 0)
    from nose.tools import assert_raises
    with assert_raises(IOError):
        open(path).read()

