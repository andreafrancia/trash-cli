import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs
from ...support.fs_fixture import FsFixture
from ...support.put.fake_fs.fake_fs import FakeFs


@pytest.mark.slow
class Test_make_unreadable_file(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        path = self.tmp_dir / "unreadable"
        fs = RealFs()
        FsFixture(fs).make_unreadable_file(self.tmp_dir / "unreadable")
        with self.assertRaises(IOError):
            RealFs().read_file(path)

    def tearDown(self):
        self.tmp_dir.clean_up()

class Test_make_unreadable_file_with_fake_fs(unittest.TestCase):
    def test(self):
        fs = FakeFs()
        FsFixture(fs).make_unreadable_file("/temp/unreadable")
        with self.assertRaises(IOError):
            fs.read_file("/temp/unreadable")