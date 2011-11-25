from nose.tools import assert_equals

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

