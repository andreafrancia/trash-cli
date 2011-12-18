from nose.tools import assert_equals

def having_file(path):
    open(path,'w').close()
    import os
    assert os.path.isfile(path)

def write_file(filename, contents):
    import os
    parent = os.path.dirname(filename)
    if not os.path.isdir(parent): os.makedirs(parent)
    file(filename, 'w').write(contents)
    assert_equals(file(filename).read(), contents)

def require_empty_dir(dirname):
    import os
    import shutil
    if os.path.exists(dirname): shutil.rmtree(dirname)
    os.makedirs(dirname)
    assert os.path.isdir(dirname)

def make_sticky_dir(path):
    import os
    os.mkdir(path)
    set_sticky_bit(path)

def set_sticky_bit(path):
    import os
    import stat
    os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

