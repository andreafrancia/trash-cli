import unittest

from tests.support.files import make_file
from tests.support.dirs.my_path import MyPath
from trashcli.fs import move, read_file


class TestMove(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_two_files(self):
        make_file(self.tmp_dir / 'a', "AAAA")
        make_file(self.tmp_dir / 'b', "BBBB")

        result = read_file(self.tmp_dir / 'b')

        assert result == 'BBBB'

    def test_move(self):
        make_file(self.tmp_dir / 'a', "AAAA")
        make_file(self.tmp_dir / 'b', "BBBB")

        move(self.tmp_dir / 'a', self.tmp_dir / 'b')

        result = read_file(self.tmp_dir / 'b')
        assert result == 'AAAA'


    def tearDown(self):
        self.tmp_dir.clean_up()
