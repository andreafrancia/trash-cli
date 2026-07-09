import errno
import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real_fs_operations import RealAtomicWrite, RealReadFile

atomic_write = RealAtomicWrite().atomic_write
open_for_write_in_exclusive_and_create_mode = RealAtomicWrite().open_for_write_in_exclusive_and_create_mode
read_file = RealReadFile().read_file


@pytest.mark.slow
class Test_atomic_write(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()

    def test_the_second_open_should_fail(self):
        path = self.temp_dir / "a"
        file_handle = open_for_write_in_exclusive_and_create_mode(path)
        try:
            open_for_write_in_exclusive_and_create_mode(path)
            self.fail()
        except OSError as e:
            assert e.errno == errno.EEXIST
        os.close(file_handle)

    def test_short_filename(self):
        path = self.temp_dir / 'a'

        atomic_write(path, b'contents')

        assert 'contents' == read_file(path)

    def test_too_long_filename(self):
        path = self.temp_dir / ('a' * 2000)

        try:
            atomic_write(path, b'contents')
            self.fail()
        except OSError as e:
            assert e.errno == errno.ENAMETOOLONG

    def test_filename_already_taken(self):
        atomic_write(self.temp_dir / "a", b'contents')

        try:
            atomic_write(self.temp_dir / "a", b'contents')
            self.fail()
        except OSError as e:
            assert e.errno == errno.EEXIST

    def tearDown(self):
        self.temp_dir.clean_up()
