import unittest

import pytest
from trashcli.fs import  read_file

from ...support.files import make_unreadable_file
from tests.support.dirs.my_path import MyPath


@pytest.mark.slow
class Test_make_unreadable_file(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        path = self.tmp_dir / "unreadable"
        make_unreadable_file(self.tmp_dir / "unreadable")
        with self.assertRaises(IOError):
            read_file(path)

    def tearDown(self):
        self.tmp_dir.clean_up()
