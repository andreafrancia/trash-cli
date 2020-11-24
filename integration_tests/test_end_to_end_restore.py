import shutil
import unittest
import subprocess
from subprocess import PIPE

from integration_tests.files import write_file
from trashcli import base_dir
import tempfile
import os

class TestEndToEndRestore(unittest.TestCase):
    def setUp(self):
        self.tmpdir = os.path.realpath(tempfile.mkdtemp())

    def test(self):
        result = subprocess.run(["python", "%s/trash-restore" % base_dir],
                                stdout=PIPE, stderr=PIPE, cwd=self.tmpdir)
        self.assertEqual("""\
No files trashed from current dir ('%s')
""" % self.tmpdir, result.stdout.decode('utf-8'))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
