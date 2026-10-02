import errno
import os
import shutil
import unittest


from tests.support.files import FsFixture, remove_file2
from tests.support.dirs.my_path import MyPath


class Test_make_unreadable_dir(unittest.TestCase):
    def setUp(self):
        self.fsx = FsFixture()
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'unreadable-dir'

        self.fsx.make_unreadable_dir(self.unreadable_dir)

    def test_the_directory_has_been_created(self):
        assert os.path.exists(self.unreadable_dir)

    def test_and_can_not_be_removed(self):
        try:
            remove_file2(self.unreadable_dir)
            self.fail()
        except OSError as e:
            self.assertEqual(errno.errorcode[e.errno], 'EACCES')

    def tearDown(self):
        self.fsx.make_readable(self.unreadable_dir)
        shutil.rmtree(self.unreadable_dir)
        self.tmp_dir.clean_up()
