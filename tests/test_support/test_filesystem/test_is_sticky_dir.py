# Copyright (C) 2008-2021 Andrea Francia Bereguardo(PV) Italy
import unittest

from tests.support.dirs.my_path import MyPath
from tests.test_support.test_filesystem.real_fs_1 import RealFs1


class TestIsStickyDir:

    def setup_method(self):
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

    def tear_down_method(self):
        self.temp_dir.clean_up()
