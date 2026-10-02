import os
import shutil

import pytest

from trashcli.fslib.real.real_fs import RealFs

from trashcli.fslib.real.real_has_sticky_bit import RealHasStickyBit
from trashcli.fslib.real.real_remove_file2 import RealRemoveFile2


class FsFixture:
    def __init__(self):
        self.fs = RealFs()
    def mkdir_p(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def make_empty_dir(self, path):
        os.mkdir(path)
        check_empty_dir(path)

    def remove_file2(self, path):
        RealRemoveFile2().remove_file2(path)

    def does_not_exist(self, path):
        assert not os.path.exists(path)

    def is_a_symlink_to_a_dir(self, path):
        dest = "%s-dest" % path
        os.mkdir(dest)
        rel_dest = os.path.basename(dest)
        os.symlink(rel_dest, path)

    def make_parent_for(self, path):
        parent = os.path.dirname(os.path.realpath(path))
        make_dirs(parent)

    def make_unreadable_file(self, path):
        make_file(path, '')
        import os
        os.chmod(path, 0)

    def set_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

    def unset_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode & ~ stat.S_ISVTX)

    def check_empty_dir(self, path):
        assert os.path.isdir(path)
        assert [] == sorted(os.listdir(path))

    def make_unsticky_dir(self, path):
        os.mkdir(path)
        unset_sticky_bit(path)

    def make_sticky_dir(self, path):
        os.mkdir(path)
        set_sticky_bit(path)

    def make_readable(self, path):
        os.chmod(path, 0o700)

    def make_unreadable_dir(self, path):
        self.fs.mkdirs(path)
        os.chmod(path, 0o300)

    def make_dirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        assert os.path.isdir(path)

    def require_empty_dir(self, path):
        if os.path.exists(path): shutil.rmtree(path)
        make_dirs(path)
        check_empty_dir(path)

    def make_empty_file(self, path):
        make_file(path, '')

    def make_file(self, filename, contents=''):
        make_parent_for(filename)
        self.fs.write_file(filename, contents)


def make_empty_file(path):
    FsFixture().make_empty_file(path)


def make_file(filename, contents=''):
    FsFixture().make_file(filename, contents)


def require_empty_dir(path):
    FsFixture().require_empty_dir(path)


def make_empty_dir(path):
    FsFixture().make_empty_dir(path)


def check_empty_dir(path):
    FsFixture().check_empty_dir(path)


def make_dirs(path):
    FsFixture().make_dirs(path)


def make_parent_for(path):
    FsFixture().make_parent_for(path)


def make_sticky_dir(path):
    FsFixture().make_sticky_dir(path)


def make_unsticky_dir(path):
    FsFixture().make_unsticky_dir(path)


def set_sticky_bit(path):
    FsFixture().set_sticky_bit(path)


def unset_sticky_bit(path):
    FsFixture().unset_sticky_bit(path)


def make_unreadable_file(path):
    FsFixture().make_unreadable_file(path)


def make_unreadable_dir(path):
    FsFixture().make_unreadable_dir(path)


def make_readable(path):
    FsFixture().make_readable(path)


def does_not_exist(path):
    FsFixture().does_not_exist(path)


def is_a_symlink_to_a_dir(path):
    FsFixture().is_a_symlink_to_a_dir(path)



def remove_file2(path):
    FsFixture().remove_file2(path)


def mkdirs(path):
    RealFs().mkdirs(path)


def write_file(filename, contents):
    RealFs().write_file(filename, contents)


def remove_file(path):
    RealFs().remove_file(path)


def read_file(path):
    return RealFs().read_file(path)


@pytest.fixture
def fsx():
    return FsFixture()
