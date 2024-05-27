import errno
import shutil
import unittest

from tests.support.dirs.my_path import MyPath
from trashcli.put.fs.real_fs import RealFs
from ...support.fs_fixture import FsFixture
from ...support.put.fake_fs.fake_fs import FakeFs


class Test_make_unreadable_dirRealFs(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'unreadable-dir'
        self.fs = RealFs()
        self.fx = FsFixture(self.fs)
        self.fx.make_unreadable_dir(self.unreadable_dir)

    def test_the_directory_has_been_created(self):
        assert self.fs.exists(self.unreadable_dir)

    def test_and_can_not_be_removed(self):
        try:
            self.fs.remove_file2(self.unreadable_dir)
            self.fail()
        except OSError as e:
            self.assertEqual(errno.errorcode[e.errno], 'EACCES')

    def tearDown(self):
        self.fx.make_readable(self.unreadable_dir)
        shutil.rmtree(self.unreadable_dir)
        self.tmp_dir.clean_up()

class Test_make_unreadable_dir_FakeFs(unittest.TestCase):
    def setUp(self):
        self.unreadable_dir = '/temp/unreadable-dir'
        self.fs = FakeFs()
        FsFixture(self.fs).make_unreadable_dir(self.unreadable_dir)

    def test_the_directory_has_been_created(self):
        assert self.fs.exists(self.unreadable_dir)

    def test_and_can_not_be_removed(self):
        try:
            self.fs.listdir(self.unreadable_dir)
            self.fail()
        except OSError as e:
            self.assertEqual(errno.errorcode[e.errno], 'EACCES')
