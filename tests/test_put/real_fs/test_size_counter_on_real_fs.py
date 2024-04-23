import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.size_counter import SizeCounter
from trashcli.put.fs.real_fs import RealFs


@pytest.mark.slow
class TestSizeCounterOnRealFs(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.counter = SizeCounter(self.fs)
        self.tmp_dir = MyPath.make_temp_dir()

    def test_a_single_file(self):
        self.fs.make_file(self.tmp_dir / 'file', 10 * 'a')

        assert self.counter.get_size_recursive(self.tmp_dir / 'file') == 10

    def test_two_files(self):
        self.fs.make_file(self.tmp_dir / 'a', 100 * 'a')
        self.fs.make_file(self.tmp_dir / 'b', 23 * 'b')

        assert self.counter.get_size_recursive(self.tmp_dir) == 123

    def test_recursive(self):
        self.fs.make_file(self.tmp_dir / 'a', 3 * '-')
        self.fs.makedirs(self.tmp_dir / 'dir', 0o777)
        self.fs.make_file(self.tmp_dir / 'dir' / 'a', 20 * '-')
        self.fs.makedirs(self.tmp_dir / 'dir' / 'dir', 0o777)
        self.fs.make_file(self.tmp_dir / 'dir' / 'dir' / 'b', 100 * '-')

        assert self.counter.get_size_recursive(self.tmp_dir) == 123

    def tearDown(self):
        self.tmp_dir.clean_up()
