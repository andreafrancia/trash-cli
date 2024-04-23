import unittest

from tests.support.dirs.my_path import MyPath
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.put.fs.size_counter import SizeCounter


class TestSizeCounterOnFakeFs(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.counter = SizeCounter(self.fs)
        self.fs.makedirs('/tmp', 0o777)
        self.tmp_dir = MyPath('/tmp')

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
