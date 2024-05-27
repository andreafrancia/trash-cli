import unittest

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from trashcli.put.fs.real_fs import RealFs


class TestMove(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fs = RealFs()
        self.fx = FsFixture(self.fs)

    def test_two_files(self):
        self.fx.make_file(self.tmp_dir / 'a', b"AAAA")
        self.fx.make_file(self.tmp_dir / 'b', b"BBBB")

        result = self.fs.read_file(self.tmp_dir / 'b')

        assert result == b'BBBB'

    def test_move(self):
        self.fx.make_file(self.tmp_dir / 'a', b"AAAA")
        self.fx.make_file(self.tmp_dir / 'b', b"BBBB")

        self.fs.move(self.tmp_dir / 'a', self.tmp_dir / 'b')

        result = self.fs.read_file(self.tmp_dir / 'b')
        assert result == b'AAAA'


    def tearDown(self):
        self.tmp_dir.clean_up()
