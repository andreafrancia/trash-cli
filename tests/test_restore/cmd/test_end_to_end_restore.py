import os
from datetime import datetime
from os.path import exists as file_exists
from os.path import join as pj

import pytest

from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.dirs.my_path import MyPath
from tests.support.run.run_command import run_command
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class TestEndToEndRestore:
    def setup_method(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()
        self.curdir = self.tmp_dir / "cwd"
        self.trash_dir = self.tmp_dir / "trash-dir"
        os.makedirs(self.curdir)
        self.fake_trash_dir = FakeTrashDir(self.trash_dir)

    def test_no_file_trashed(self):
        result = self.run_command("trash-restore")

        assert result.output() == """\
No files trashed from current dir ('%s')
""" % self.curdir

    def test_original_file_not_existing(self):
        self.fake_trash_dir.add_trashinfo3("foo", "/path", datetime(2000,1,1,0,0,1))

        result = self.run_command("trash-restore", ["/"], input='0')

        assert result.output() == (
            "   0 2000-01-01 00:00:01 /path\n"
            "What file to restore [0..0]: \n"
            "[Errno 2] No such file or directory: '%s/files/foo'\n" %
            self.trash_dir)

    def test_restore_happy_path(self):
        self.fake_trash_dir.add_trashed_file(
            "file1", pj(self.curdir, "path", "to", "file1"), "contents")
        self.fake_trash_dir.add_trashed_file(
            "file2", pj(self.curdir, "path", "to", "file2"), "contents")
        assert file_exists(pj(self.trash_dir, "info", "file2.trashinfo"))
        assert file_exists(pj(self.trash_dir, "files", "file2"))

        result = self.run_command("trash-restore", ["/", '--sort=path'], input='1')

        assert result.stdout == """\
   0 2000-01-01 00:00:01 %(curdir)s/path/to/file1
   1 2000-01-01 00:00:01 %(curdir)s/path/to/file2
What file to restore [0..1]: """ % {'curdir': self.curdir}
        assert result.stderr == ""
        assert self.fs.read_file(pj(self.curdir, "path/to/file2")) == "contents"
        assert not file_exists(pj(self.trash_dir, "info", "file2.trashinfo"))
        assert not file_exists(pj(self.trash_dir, "files", "file2"))

    def test_restore_with_relative_path(self):
        self.fake_trash_dir.add_trashed_file(
            "file1", pj(self.curdir, "path", "to", "file1"), "contents")
        assert file_exists(pj(self.trash_dir, "info", "file1.trashinfo"))
        assert file_exists(pj(self.trash_dir, "files", "file1"))

        result = self.run_command("trash-restore",
                                  ["%(curdir)s" % {'curdir': "."},
                                   '--sort=path'], input='0')

        assert result.stdout == """\
   0 2000-01-01 00:00:01 %(curdir)s/path/to/file1
What file to restore [0..0]: """ % {'curdir': self.curdir}
        assert result.stderr == ""
        assert self.fs.read_file(pj(self.curdir, "path/to/file1")) == "contents"
        assert not file_exists(pj(self.trash_dir, "info", "file1.trashinfo"))
        assert not file_exists(pj(self.trash_dir, "files", "file1"))

    def run_command(self, command, args=None, input=''):
        if args is None:
            args = []
        return run_command(self.curdir, command,
                           ["--trash-dir", self.trash_dir] + args, input)

    def teardown_method(self):
        self.tmp_dir.clean_up()
