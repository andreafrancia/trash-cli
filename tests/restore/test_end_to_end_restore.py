import unittest

import pytest

from ..fake_trash_dir import FakeTrashDir, a_trashinfo
from trashcli.fs import read_file
from ..support import MyPath
import os
from os.path import join as pj
from os.path import exists as file_exists
from .. import run_command


@pytest.mark.slow
class TestEndToEndRestore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.curdir = self.tmp_dir / "cwd"
        self.trash_dir = self.tmp_dir / "trash-dir"
        os.makedirs(self.curdir)
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_no_file_trashed(self):
        result = self.run_command("trash-restore")

        self.assertEqual("""\
No files trashed from current dir ('%s')
""" % self.curdir, result.stdout)

    def test_original_file_not_existing(self):
        self.fake_trash_dir.add_trashinfo(contents=a_trashinfo("/path"), basename='foo')

        result = self.run_command("trash-restore", ["/"], input='0')

        self.assertEqual("""\
   0 2000-01-01 00:00:01 /path
What file to restore [0..0]: """,
                         result.stdout)
        self.assertEqual("[Errno 2] No such file or directory: '%s/files/foo'\n" %
                         self.trash_dir,
                         result.stderr)

    def test_restore_happy_path(self):
        self.fake_trash_dir.add_trashed_file(
            "file1", pj(self.curdir, "path", "to", "file1"), "contents")
        self.fake_trash_dir.add_trashed_file(
            "file2", pj(self.curdir, "path", "to", "file2"), "contents")
        self.assertEqual(True, file_exists(pj(self.trash_dir, "info", "file2.trashinfo")))
        self.assertEqual(True, file_exists(pj(self.trash_dir, "files", "file2")))

        result = self.run_command("trash-restore", ["/", '--sort=path'], input='1')

        self.assertEqual("""\
   0 2000-01-01 00:00:01 %(curdir)s/path/to/file1
   1 2000-01-01 00:00:01 %(curdir)s/path/to/file2
What file to restore [0..1]: """ % { 'curdir': self.curdir},
                         result.stdout)
        self.assertEqual("", result.stderr)
        self.assertEqual("contents", read_file(pj(self.curdir, "path/to/file2")))
        self.assertEqual(False, file_exists(pj(self.trash_dir, "info", "file2.trashinfo")))
        self.assertEqual(False, file_exists(pj(self.trash_dir, "files", "file2")))

    def test_restore_with_relative_path(self):
        self.fake_trash_dir.add_trashed_file(
            "file1", pj(self.curdir, "path", "to", "file1"), "contents")
        self.assertEqual(True, file_exists(pj(self.trash_dir, "info", "file1.trashinfo")))
        self.assertEqual(True, file_exists(pj(self.trash_dir, "files", "file1")))

        result = self.run_command("trash-restore",
                                  ["%(curdir)s" % {'curdir': "."},
                                   '--sort=path'], input='0')

        self.assertEqual("""\
   0 2000-01-01 00:00:01 %(curdir)s/path/to/file1
What file to restore [0..0]: """ % {'curdir': self.curdir},
                         result.stdout)
        self.assertEqual("", result.stderr)
        self.assertEqual("contents", read_file(pj(self.curdir, "path/to/file1")))
        self.assertEqual(False, file_exists(pj(self.trash_dir, "info", "file1.trashinfo")))
        self.assertEqual(False, file_exists(pj(self.trash_dir, "files", "file1")))

    def run_command(self, command, args=None, input=''):
        if args is None:
            args = []
        return run_command.run_command(self.curdir,
                                       command,
                                       ["--trash-dir", self.trash_dir] + args,
                                       input)

    def tearDown(self):
        self.tmp_dir.clean_up()
