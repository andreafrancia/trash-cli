# Copyright (C) 2008-2021 Andrea Francia Bereguardo(PV) Italy

import os
import unittest

import pytest

from trashcli.fs import has_sticky_bit, mkdirs, is_sticky_dir
from .support.files import make_empty_file, set_sticky_bit, unset_sticky_bit
from .support.my_path import MyPath


@pytest.mark.slow
class TestWithInSandbox(unittest.TestCase):

    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()

    def test_mkdirs_with_default_mode(self):
        mkdirs(self.temp_dir / "test-dir/sub-dir")

        assert os.path.isdir(self.temp_dir / "test-dir/sub-dir")

    def test_has_sticky_bit_returns_true(self):
        make_empty_file(self.temp_dir / "sticky")
        set_sticky_bit(self.temp_dir / "sticky")

        assert has_sticky_bit(self.temp_dir / 'sticky')

    def test_has_sticky_bit_returns_false(self):
        make_empty_file(self.temp_dir / "non-sticky")
        set_sticky_bit(self.temp_dir / "non-sticky")
        unset_sticky_bit(self.temp_dir / "non-sticky")

        assert not has_sticky_bit(self.temp_dir / "non-sticky")

    def tearDown(self):
        self.temp_dir.clean_up()


class Test_is_sticky_dir(unittest.TestCase):

    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()

    def test_dir_non_sticky(self):
        mkdirs(self.temp_dir / 'dir')

        assert not is_sticky_dir(self.temp_dir / 'dir')

    def test_dir_sticky(self):
        mkdirs(self.temp_dir / 'dir')
        set_sticky_bit(self.temp_dir / 'dir')

        assert is_sticky_dir(self.temp_dir / 'dir')

    def test_non_dir_but_sticky(self):
        make_empty_file(self.temp_dir / 'dir')
        set_sticky_bit(self.temp_dir / 'dir')

        assert not is_sticky_dir(self.temp_dir / 'dir')

    def tearDown(self):
        self.temp_dir.clean_up()
