import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from tests.test_support.test_filesystem.real_fs_1 import RealFs1


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
