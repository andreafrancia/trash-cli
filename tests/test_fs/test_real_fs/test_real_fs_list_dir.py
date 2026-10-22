import unittest

import pytest

from tests.support.dirs.temp_dir import make_temp_dir
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class TestRealFsListDir(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.tmp_dir = make_temp_dir(RealFs())

    def test(self):
        self.fs.write_file(self.tmp_dir / 'a' , 'content')
        self.fs.write_file(self.tmp_dir / 'b' , 'content')
        self.fs.write_file(self.tmp_dir / 'c', 'content')
        self.fs.makedirs(self.tmp_dir / 'd', 0o700)

        assert sorted(self.fs.listdir(self.tmp_dir)) == ['a', 'b', 'c', 'd']

    def tearDown(self):
        self.tmp_dir.clean_up()
