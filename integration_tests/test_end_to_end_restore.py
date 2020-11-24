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
        result = self.run_command("trash-restore")

        self.assertEqual("""\
No files trashed from current dir ('%s')
""" % self.tmpdir, result.stdout.decode('utf-8'))

    def run_command(self, command):
        command_full_path = os.path.join(base_dir, command)
        return subprocess.run(["python", command_full_path],
                              stdout=PIPE, stderr=PIPE, cwd=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
