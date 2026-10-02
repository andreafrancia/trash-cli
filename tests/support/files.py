import os
import shutil

import pytest

from trashcli.fslib.real.real_fs import RealFs

from trashcli.fslib.real.real_has_sticky_bit import RealHasStickyBit
from trashcli.fslib.real.real_remove_file2 import RealRemoveFile2


class FsFixture:
    def __init__(self, fs):  # type: (RealFs) -> None
        self.fs = fs

    def mkdir_p(self, path):
        if not self.fs.path_isdir(path):
            self.fs.makedirs(path, 0o777)

    def make_empty_dir(self, path):
        self.fs.mkdir(path)
        self.check_empty_dir(path)

    def remove_file2(self, path):
        RealRemoveFile2().remove_file2(path)

    def does_not_exist(self, path):
        assert not self.fs.path_exists(path)

    def is_a_symlink_to_a_dir(self, path):
        dest = "%s-dest" % path
        self.fs.mkdir(dest)
        rel_dest = os.path.basename(dest)
        self.fs.symlink(rel_dest, path)

    def make_parent_for(self, path):
        parent = os.path.dirname(os.path.realpath(path))
        self.make_dirs(parent)

    def make_unreadable_file(self, path):
        self.make_file(path, '')
        import os
        os.chmod(path, 0)

    def set_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

    def unset_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode & ~ stat.S_ISVTX)

    def check_empty_dir(self, path):
        assert self.fs.path_isdir(path)
        assert [] == sorted(self.fs.listdir(path))

    def make_unsticky_dir(self, path):
        self.fs.mkdir(path)
        self.unset_sticky_bit(path)

    def make_sticky_dir(self, path):
        self.fs.mkdir(path)
        self.set_sticky_bit(path)

    def make_readable(self, path):
        os.chmod(path, 0o700)

    def make_unreadable_dir(self, path):
        self.fs.mkdirs(path)
        os.chmod(path, 0o300)

    def make_dirs(self, path):
        if not self.fs.path_isdir(path):
            self.fs.makedirs(path, 0o777)
        assert self.fs.path_isdir(path)

    def require_empty_dir(self, path):
        if os.path.exists(path): shutil.rmtree(path)
        self.make_dirs(path)
        self.check_empty_dir(path)

    def make_empty_file(self, path):
        self.make_file(path, '')

    def make_file(self, filename, contents=''):
        self.make_parent_for(filename)
        self.fs.write_file(filename, contents)


@pytest.fixture
def fsx():
    return FsFixture(RealFs())
