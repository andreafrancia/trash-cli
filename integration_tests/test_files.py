import errno
import os
import shutil
import unittest

from integration_tests.files import make_unreadable_file, make_unreadable_dir,\
    make_readable
from trashcli.fs import read_file, FileRemover
from unit_tests.support import MyPath


class Test_make_unreadable_file(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        path = self.tmp_dir / "unreadable"
        make_unreadable_file(self.tmp_dir / "unreadable")
        with self.assertRaises(IOError):
            read_file(path)

    def tearDown(self):
        self.tmp_dir.clean_up()


class Test_make_unreadable_dir(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'unreadable-dir'

        make_unreadable_dir(self.unreadable_dir)

    def test_the_directory_has_been_created(self):
        assert os.path.exists(self.unreadable_dir)

    def test_and_can_not_be_removed(self):
        try:
            FileRemover().remove_file(self.unreadable_dir)
            self.fail()
        except OSError as e:
            self.assertEqual(errno.errorcode[e.errno], 'EACCES')

    def tearDown(self):
        make_readable(self.unreadable_dir)
        shutil.rmtree(self.unreadable_dir)
