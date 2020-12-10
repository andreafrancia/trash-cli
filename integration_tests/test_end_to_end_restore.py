import shutil
import unittest
import subprocess
from subprocess import PIPE

from integration_tests.fake_trash_dir import FakeTrashDir, a_trashinfo
from trashcli import base_dir
import tempfile
import os

class TestEndToEndRestore(unittest.TestCase):
    def setUp(self):
        self.tmpdir = os.path.realpath(tempfile.mkdtemp())
        self.curdir = os.path.join(self.tmpdir, "cwd")
        self.trash_dir = os.path.join(self.tmpdir, "trash-dir")
        os.makedirs(self.curdir)

    def test(self):
        result = self.run_command("trash-restore")

        self.assertEqual("""\
No files trashed from current dir ('%s')
""" % self.curdir, result.stdout.decode('utf-8'))

    def test2(self):
        trash_dir = FakeTrashDir(self.trash_dir)
        trash_dir.add_trashinfo(a_trashinfo("/path"))

        result = self.run_command("trash-restore", ["/"], input='0')

        self.assertEqual("""\
   0 2000-01-01 00:00:01 /path
What file to restore [0..0]: """,
                         result.stdout.decode('utf-8'))
        self.assertEqual("[Errno 2] No such file or directory: '%s/files/1'\n" %
                         self.trash_dir,
                         result.stderr.decode('utf-8'))

    def run_command(self, command, args=None, input=''):
        class Result:
            def __init__(self, stdout, stderr):
                self.stdout = stdout
                self.stderr = stderr
        if args == None:
            args = []
        command_full_path = os.path.join(base_dir, command)
        process = subprocess.Popen(["python", command_full_path,
                                    "--trash-dir", self.trash_dir] + args,
                                   stdin=PIPE,
                                   stdout=PIPE,
                                   stderr=PIPE, cwd=self.curdir)
        stdout, stderr = process.communicate(input=input.encode('utf-8'))

        return Result(stdout, stderr)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
