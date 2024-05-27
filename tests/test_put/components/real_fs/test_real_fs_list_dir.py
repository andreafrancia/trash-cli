import unittest

from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs


class TestRealFsListDir(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        self.fs.make_file(self.tmp_dir / 'a' , b'content')
        self.fs.make_file(self.tmp_dir / 'b' , b'content')
        self.fs.make_file(self.tmp_dir / 'c', b'content')
        self.fs.makedirs(self.tmp_dir / 'd', 0o700)

        assert sorted(self.fs.listdir(self.tmp_dir)) == ['a', 'b', 'c', 'd']

    def tearDown(self):
        self.tmp_dir.clean_up()
