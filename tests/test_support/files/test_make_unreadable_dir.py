import errno
import os
import shutil
import unittest

from trashcli.fs import remove_file2

from ...support.files import make_unreadable_dir, \
    make_readable
from tests.support.dirs.my_path import MyPath


class Test_make_unreadable_dir(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'unreadable-dir'

        make_unreadable_dir(self.unreadable_dir)

    def test_the_directory_has_been_created(self):
        assert os.path.exists(self.unreadable_dir)

    def test_and_can_not_be_removed(self):
        try:
            remove_file2(self.unreadable_dir)
            self.fail()
        except OSError as e:
            self.assertEqual(errno.errorcode[e.errno], 'EACCES')

    def tearDown(self):
        make_readable(self.unreadable_dir)
        shutil.rmtree(self.unreadable_dir)
        self.tmp_dir.clean_up()
