import errno
import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs


@pytest.mark.slow
class Test_atomic_write(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.fs = RealFs()

    def test_the_second_open_should_fail(self):
        path = self.temp_dir / "a"
        file_handle = self.fs.open_for_write_in_exclusive_and_create_mode(path)
        try:
            self.fs.open_for_write_in_exclusive_and_create_mode(path)
            self.fail()
        except OSError as e:
            assert e.errno == errno.EEXIST
        os.close(file_handle)

    def test_short_filename(self):
        path = self.temp_dir / 'a'

        self.fs.atomic_write(path, b'contents')

        assert b'contents' == self.fs.read_file(path)

    def test_too_long_filename(self):
        path = self.temp_dir / ('a' * 2000)

        try:
            self.fs.atomic_write(path, b'contents')
            self.fail()
        except OSError as e:
            assert e.errno == errno.ENAMETOOLONG

    def test_filename_already_taken(self):
        self.fs.atomic_write(self.temp_dir / "a", b'contents')

        try:
            self.fs.atomic_write(self.temp_dir / "a", b'contents')
            self.fail()
        except OSError as e:
            assert e.errno == errno.EEXIST

    def tearDown(self):
        self.temp_dir.clean_up()
