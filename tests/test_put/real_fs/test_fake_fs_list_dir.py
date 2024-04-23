import unittest

from tests.support.dirs.my_path import MyPath
from tests.test_put.support.fake_fs.fake_fs import FakeFs


class TestFakeFsListDir(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.tmp_dir = MyPath('/tmp')
        self.fs.makedirs(self.tmp_dir, 0o700)

    def test(self):
        self.fs.make_file(self.tmp_dir / 'a', 'content')
        self.fs.make_file(self.tmp_dir / 'b', 'content')
        self.fs.make_file(self.tmp_dir / 'c', 'content')
        self.fs.makedirs(self.tmp_dir / 'd', 0o700)

        assert sorted(self.fs.listdir(self.tmp_dir)) == ['a', 'b', 'c', 'd']
