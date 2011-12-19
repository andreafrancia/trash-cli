# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals
import os, shutil

def having_file(path):
    make_dirs(os.path.dirname(path))
    open(path,'w').close()
    assert os.path.isfile(path)

def write_file(filename, contents):
    parent = os.path.dirname(filename)
    if not os.path.isdir(parent): os.makedirs(parent)
    file(filename, 'w').write(contents)
    assert_equals(file(filename).read(), contents)

def require_empty_dir(path):
    if os.path.exists(path): shutil.rmtree(path)
    make_dirs(path)

def make_dirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    assert os.path.isdir(path)

def make_sticky_dir(path):
    os.mkdir(path)
    set_sticky_bit(path)

def set_sticky_bit(path):
    import stat
    os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

