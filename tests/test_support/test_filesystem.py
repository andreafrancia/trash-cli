# Copyright (C) 2008-2021 Andrea Francia Bereguardo(PV) Italy

import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real_fs_operations import RealHasStickyBit, RealMkDirs, \
    RealWriteFile, RealIsStickyDir


class RealFs1:
    def has_sticky_bit(self, path):
        return RealHasStickyBit().has_sticky_bit(path)

    def mkdirs(self, path):
        RealMkDirs().mkdirs(path)

    def make_file(self, filename, contents=''):
        self.make_parent_for(filename)
        self.write_file(filename, contents)

    def make_parent_for(self, path):
        parent = os.path.dirname(os.path.realpath(path))
        self.make_dirs(parent)

    def write_file(self, filename, contents):
        RealWriteFile().write_file(filename, contents)

    def make_dirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        assert os.path.isdir(path)

    def set_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

    def make_empty_file(self, path):
        self.make_file(path, '')

    def unset_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode & ~ stat.S_ISVTX)

    def is_sticky_dir(self, path):
        return RealIsStickyDir().is_sticky_dir(path)


@pytest.mark.slow
class TestWithInSandbox(unittest.TestCase):

    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.fs = RealFs1()

    def test_mkdirs_with_default_mode(self):
        self.fs.mkdirs(self.temp_dir / "test-dir/sub-dir")

        assert os.path.isdir(self.temp_dir / "test-dir/sub-dir")

    def test_has_sticky_bit_returns_true(self):
        self.fs.make_empty_file(self.temp_dir / "sticky")
        self.fs.set_sticky_bit(self.temp_dir / "sticky")

        assert self.fs.has_sticky_bit(self.temp_dir / 'sticky')

    def test_has_sticky_bit_returns_false(self):
        self.fs.make_empty_file(self.temp_dir / "non-sticky")
        self.fs.set_sticky_bit(self.temp_dir / "non-sticky")
        self.fs.unset_sticky_bit(self.temp_dir / "non-sticky")

        assert not self.fs.has_sticky_bit(self.temp_dir / "non-sticky")

    def tearDown(self):
        self.temp_dir.clean_up()


class Test_is_sticky_dir(unittest.TestCase):

    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.fs = RealFs1()

    def test_dir_non_sticky(self):
        self.fs.mkdirs(self.temp_dir / 'dir')

        assert not self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def test_dir_sticky(self):
        self.fs.mkdirs(self.temp_dir / 'dir')
        self.fs.set_sticky_bit(self.temp_dir / 'dir')

        assert self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def test_non_dir_but_sticky(self):
        self.fs.make_empty_file(self.temp_dir / 'dir')
        self.fs.set_sticky_bit(self.temp_dir / 'dir')

        assert not self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def tearDown(self):
        self.temp_dir.clean_up()
