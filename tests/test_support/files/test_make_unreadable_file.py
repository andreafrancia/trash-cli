import unittest

import pytest

from tests.support.files import FsFixture
from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class Test_make_unreadable_file(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.fsx = FsFixture(RealFs())
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        path = self.tmp_dir / "unreadable"
        self.fsx.make_unreadable_file(self.tmp_dir / "unreadable")
        with self.assertRaises(IOError):
            self.fs.read_file(path)

    def tearDown(self):
        self.tmp_dir.clean_up()
