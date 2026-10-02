import unittest

import pytest

from tests.support.files import FsFixture, read_file
from tests.support.dirs.my_path import MyPath


@pytest.mark.slow
class Test_make_unreadable_file(unittest.TestCase):
    def setUp(self):
        self.fsx = FsFixture()
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        path = self.tmp_dir / "unreadable"
        self.fsx.make_unreadable_file(self.tmp_dir / "unreadable")
        with self.assertRaises(IOError):
            read_file(path)

    def tearDown(self):
        self.tmp_dir.clean_up()
