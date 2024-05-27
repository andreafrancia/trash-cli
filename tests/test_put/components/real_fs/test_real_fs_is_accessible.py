import os
import unittest

from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs


class TestRealFsIsAccessible(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()

    def test_dangling_link(self):
        os.symlink('non-existent', self.tmp_dir / 'link')

        result = self.fs.is_accessible(self.tmp_dir / 'link')

        assert result is False

    def test_connected_link(self):
        self.fs.make_file(self.tmp_dir / 'link-target', b'')
        os.symlink('link-target', self.tmp_dir / 'link')

        result = self.fs.is_accessible(self.tmp_dir / 'link')

        assert result is True

    def test_dangling_link_with_lexists(self):
        os.symlink('non-existent', self.tmp_dir / 'link')

        result = self.fs.lexists(self.tmp_dir / 'link')

        assert result is True

    def test_connected_link_with_lexists(self):
        self.fs.make_file(self.tmp_dir / 'link-target', b'')
        os.symlink('link-target', self.tmp_dir / 'link')

        result = self.fs.lexists(self.tmp_dir / 'link')

        assert result is True
