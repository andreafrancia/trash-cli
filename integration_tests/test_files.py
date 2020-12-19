import os
import shutil
import tempfile
import unittest

from integration_tests.files import make_unreadable_file, read_file


class Test_make_unreadable_file(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test(self):
        path = os.path.join(self.tmp, "unreadable")
        make_unreadable_file(path)
        with self.assertRaises(OSError):
            read_file(path)

    def tearDown(self):
        shutil.rmtree(self.tmp)