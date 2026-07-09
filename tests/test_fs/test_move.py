import unittest

from tests.support.files import make_file
from tests.support.dirs.my_path import MyPath
from trashcli.fslib.fs_operations import RealMove
from trashcli.fslib.real_fs_operations import RealReadFile

move = RealMove().move
read_file = RealReadFile().read_file

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
