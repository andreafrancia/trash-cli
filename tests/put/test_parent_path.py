import os
import unittest

import pytest
from trashcli.put.parent_realpath import ParentRealpath

from ..files import make_empty_file, require_empty_dir
from ..support.my_path import MyPath


def parent_path(path):
    return ParentRealpath(os.path.realpath).parent_realpath(path)

@pytest.mark.slow
class Test_parent_path(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        require_empty_dir(self.tmp_dir / 'other_dir/dir')
        os.symlink(self.tmp_dir / 'other_dir/dir', self.tmp_dir / 'dir')
        make_empty_file(self.tmp_dir / 'dir/foo')
        assert (self.tmp_dir / 'other_dir/dir' == parent_path(self.tmp_dir / 'dir/foo'))

    def test2(self):
        require_empty_dir(self.tmp_dir / 'test-disk/dir')
        os.symlink(self.tmp_dir / 'test-disk/non-existent',
                   self.tmp_dir / 'link-to-non-existent')
        assert parent_path(self.tmp_dir / 'link-to-non-existent') == \
               self.tmp_dir

    def test3(self):
        require_empty_dir(self.tmp_dir / 'foo')
        require_empty_dir(self.tmp_dir / 'bar')
        os.symlink('../bar/zap', self.tmp_dir / 'foo/zap')
        assert parent_path(self.tmp_dir / 'foo/zap') == \
               os.path.join(self.tmp_dir, 'foo')

    def test4(self):
        require_empty_dir(self.tmp_dir / 'foo')
        require_empty_dir(self.tmp_dir / 'bar')
        os.symlink('../bar/zap', self.tmp_dir / 'foo/zap')
        make_empty_file(self.tmp_dir / 'bar/zap')
        assert parent_path(self.tmp_dir / 'foo/zap') == \
               os.path.join(self.tmp_dir,'foo')

    def tearDown(self):
        self.tmp_dir.clean_up()
