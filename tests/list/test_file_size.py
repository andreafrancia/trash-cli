import unittest

from tests.files import make_file
from tests.support import MyPath

from trashcli import fs


class Test_file_size(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        make_file(self.tmp_dir / 'a-file', '123')
        result = fs.file_size(self.tmp_dir / 'a-file')
        assert 3 == result

    def tearDown(self):
        self.tmp_dir.clean_up()
