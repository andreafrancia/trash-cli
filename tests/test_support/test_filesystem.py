# Copyright (C) 2008-2021 Andrea Francia Bereguardo(PV) Italy

import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from trashcli.put.fs.real_fs import RealFs


@pytest.mark.slow
class TestWithInSandbox(unittest.TestCase):

    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.fx = FsFixture(self.fs)

    def test_mkdirs_with_default_mode(self):
        self.fs.mkdirs(self.temp_dir / "test-dir/sub-dir")

        assert os.path.isdir(self.temp_dir / "test-dir/sub-dir")

    def test_has_sticky_bit_returns_true(self):
        self.fx.make_empty_file(self.temp_dir / "sticky")
        self.fs.set_sticky_bit(self.temp_dir / "sticky")
        assert self.fs.has_sticky_bit(self.temp_dir / 'sticky')

    def test_has_sticky_bit_returns_false(self):
        self.fx.make_empty_file(self.temp_dir / "non-sticky")
        self.fs.set_sticky_bit(self.temp_dir / "non-sticky")
        self.fs.unset_sticky_bit(self.temp_dir / "non-sticky")

        assert not self.fs.has_sticky_bit(self.temp_dir / "non-sticky")

    def tearDown(self):
        self.temp_dir.clean_up()


class Test_is_sticky_dir(unittest.TestCase):

    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.fx = FsFixture(self.fs)

    def test_dir_non_sticky(self):
        self.fs.mkdirs(self.temp_dir / 'dir')

        assert not self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def test_dir_sticky(self):
        self.fs.mkdirs(self.temp_dir / 'dir')
        self.fs.set_sticky_bit(self.temp_dir / 'dir')

        assert self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def test_non_dir_but_sticky(self):
        self.fx.make_empty_file(self.temp_dir / 'dir')
        self.fs.set_sticky_bit(self.temp_dir / 'dir')

        assert not self.fs.is_sticky_dir(self.temp_dir / 'dir')

    def tearDown(self):
        self.temp_dir.clean_up()
