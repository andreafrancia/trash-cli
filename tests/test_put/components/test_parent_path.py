import os
import unittest

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from trashcli.put.fs.parent_realpath import ParentRealpathFs
from trashcli.put.fs.real_fs import RealFs


def parent_path(path):
    return ParentRealpathFs(RealFs()).parent_realpath(path)


@pytest.mark.slow
class Test_parent_path(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fx = FsFixture(RealFs())

    def test(self):
        self.fx.require_empty_dir(self.tmp_dir / 'other_dir/dir')
        os.symlink(self.tmp_dir / 'other_dir/dir', self.tmp_dir / 'dir')
        self.fx.make_empty_file(self.tmp_dir / 'dir/foo')
        assert (self.tmp_dir / 'other_dir/dir' == parent_path(
            self.tmp_dir / 'dir/foo'))

    def test2(self):
        self.fx.require_empty_dir(self.tmp_dir / 'test-disk/dir')
        os.symlink(self.tmp_dir / 'test-disk/non-existent',
                   self.tmp_dir / 'link-to-non-existent')
        assert parent_path(self.tmp_dir / 'link-to-non-existent') == \
               self.tmp_dir

    def test3(self):
        self.fx.require_empty_dir(self.tmp_dir / 'foo')
        self.fx.require_empty_dir(self.tmp_dir / 'bar')
        os.symlink('../bar/zap', self.tmp_dir / 'foo/zap')
        assert parent_path(self.tmp_dir / 'foo/zap') == \
               os.path.join(self.tmp_dir, 'foo')

    def test4(self):
        self.fx.require_empty_dir(self.tmp_dir / 'foo')
        self.fx.require_empty_dir(self.tmp_dir / 'bar')
        os.symlink('../bar/zap', self.tmp_dir / 'foo/zap')
        self.fx.make_empty_file(self.tmp_dir / 'bar/zap')
        assert parent_path(self.tmp_dir / 'foo/zap') == \
               os.path.join(self.tmp_dir, 'foo')

    def tearDown(self):
        self.tmp_dir.clean_up()
