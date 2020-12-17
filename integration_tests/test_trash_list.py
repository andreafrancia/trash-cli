# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

import os
import shutil
import tempfile

from trashcli.list import ListCmd
from .files import (require_empty_dir, make_sticky_dir, make_unsticky_dir)
from .output_collector import OutputCollector
from .fake_trash_dir import (
    a_trashinfo_without_date,
    a_trashinfo_without_path,
    a_trashinfo_with_invalid_date, FakeTrashDir)
from textwrap import dedent
from trashcli.fs import FileSystemReader
from .asserts import assert_equals_with_unidiff
import unittest


class Setup(unittest.TestCase):
    def setUp(self):
        self.xdg_data_home = tempfile.mkdtemp()
        require_empty_dir('topdir')
        self.user = TrashListUser(self.xdg_data_home)
    def tearDown(self):
        shutil.rmtree(self.xdg_data_home)

def sort_lines(lines):
    return "".join(sorted(lines.splitlines(True)))

class Test_describe_trash_list(Setup):

    def test_should_output_the_help_message(self):

        self.user.run_trash_list('--help')

        assert_equals_with_unidiff(dedent("""\
            Usage: trash-list [OPTIONS...]

            List trashed files

            Options:
              --version   show program's version number and exit
              -h, --help  show this help message and exit

            Report bugs to https://github.com/andreafrancia/trash-cli/issues
        """), self.user.output())

    def test_should_output_nothing_when_trashcan_is_empty(self):

        self.user.run_trash_list()

        assert_equals_with_unidiff('', self.user.output())

    def test_should_output_deletion_date_and_path(self):
        self.user.home_trashdir.add_trashinfo2('/aboslute/path',
                                              '2001-02-03T23:55:59')

        self.user.run_trash_list()

        assert_equals_with_unidiff("2001-02-03 23:55:59 /aboslute/path\n",
                                   self.user.output())

    def test_should_output_info_for_multiple_files(self):
        self.user.home_trashdir.add_trashinfo2("/file1", "2000-01-01T00:00:01")
        self.user.home_trashdir.add_trashinfo2("/file2", "2000-01-01T00:00:02")
        self.user.home_trashdir.add_trashinfo2("/file3", "2000-01-01T00:00:03")

        self.user.run_trash_list()
        output = self.user.output()

        assert_equals_with_unidiff("2000-01-01 00:00:01 /file1\n"
                                   "2000-01-01 00:00:02 /file2\n"
                                   "2000-01-01 00:00:03 /file3\n",
                                   sort_lines(output))

    def test_should_output_unknown_dates_with_question_marks(self):
        self.user.home_trashdir.add_trashinfo(a_trashinfo_without_date())

        self.user.run_trash_list()

        assert_equals_with_unidiff("????-??-?? ??:??:?? /path\n",
                                   self.user.output())

    def test_should_output_invalid_dates_using_question_marks(self):
        self.user.home_trashdir.add_trashinfo(a_trashinfo_with_invalid_date())

        self.user.run_trash_list()

        assert_equals_with_unidiff("????-??-?? ??:??:?? /path\n",
                                   self.user.output())

    def test_should_warn_about_empty_trashinfos(self):
        self.user.home_trashdir.add_trashinfo('', 'empty')

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "Parse Error: %(XDG_DATA_HOME)s/Trash/info/empty.trashinfo: "
            "Unable to parse Path.\n" % {"XDG_DATA_HOME":self.xdg_data_home},
            self.user.error())

    def test_should_warn_about_unreadable_trashinfo(self):
        self.user.home_trashdir.add_unreadable_trashinfo('unreadable')

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "[Errno 13] Permission denied: "
            "'%(XDG_DATA_HOME)s/Trash/info/unreadable.trashinfo'\n" % {
                'XDG_DATA_HOME': self.xdg_data_home
            },
            self.user.error())

    def test_should_warn_about_unexistent_path_entry(self):
        self.user.home_trashdir.add_trashinfo(a_trashinfo_without_path())

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "Parse Error: %(XDG_DATA_HOME)s/Trash/info/1.trashinfo: "
            "Unable to parse Path.\n" % {'XDG_DATA_HOME': self.xdg_data_home},
            self.user.error())
        assert_equals_with_unidiff('', self.user.output())

class Test_with_a_top_trash_dir(Setup):
    def setUp(self):
        super(type(self),self).setUp()
        self.top_trashdir1 = FakeTrashDir('topdir/.Trash/123')
        self.user.set_fake_uid(123)
        self.user.add_volume('topdir')

    def test_should_list_its_contents_if_parent_is_sticky(self):
        make_sticky_dir('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff("2000-01-01 00:00:00 topdir/file1\n",
                                   self.user.output())

    def test_and_should_warn_if_parent_is_not_sticky(self):
        make_unsticky_dir('topdir/.Trash')
        self.and_dir_exists('topdir/.Trash/123')

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "TrashDir skipped because parent not sticky: topdir/.Trash/123\n",
            self.user.error()
        )

    def test_but_it_should_not_warn_when_the_parent_is_unsticky_but_there_is_no_trashdir(self):
        make_unsticky_dir('topdir/.Trash')
        self.but_does_not_exists_any('topdir/.Trash/123')

        self.user.run_trash_list()

        assert_equals_with_unidiff("", self.user.error())

    def test_should_ignore_trash_from_a_unsticky_topdir(self):
        make_unsticky_dir('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff('', self.user.output())

    def test_it_should_ignore_Trash_is_a_symlink(self):
        self.when_is_a_symlink_to_a_dir('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff('', self.user.output())

    def test_and_should_warn_about_it(self):
        self.when_is_a_symlink_to_a_dir('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            'TrashDir skipped because parent not sticky: topdir/.Trash/123\n',
            self.user.error()
        )

    def but_does_not_exists_any(self, path):
        assert not os.path.exists(path)
    def and_dir_exists(self, path):
        os.mkdir(path)
        assert os.path.isdir(path)
    def and_contains_a_valid_trashinfo(self):
        self.top_trashdir1.add_trashinfo2('file1', '2000-01-01T00:00:00')
    def when_is_a_symlink_to_a_dir(self, path):
        dest = "%s-dest" % path
        os.mkdir(dest)
        rel_dest = os.path.basename(dest)
        os.symlink(rel_dest, path)


class Test_describe_when_a_file_is_in_alternate_top_trashdir(Setup):

    def test_should_list_contents_of_alternate_trashdir(self):
        self.user.set_fake_uid(123)
        self.user.add_volume('topdir')
        self.top_trashdir2 = FakeTrashDir('topdir/.Trash-123')
        self.top_trashdir2.add_trashinfo2('file', '2000-01-01T00:00:00')

        self.user.run_trash_list()

        assert_equals_with_unidiff("2000-01-01 00:00:00 topdir/file\n",
                                   self.user.output())

class TrashListUser:
    def __init__(self, xdg_data_home):
        self.stdout      = OutputCollector()
        self.stderr      = OutputCollector()
        self.environ     = {'XDG_DATA_HOME': xdg_data_home}
        self.fake_getuid = self.error
        self.volumes     = []
        trash_dir = os.path.join(xdg_data_home, "Trash")
        self.home_trashdir = FakeTrashDir(trash_dir)

    def run_trash_list(self, *args):
        self.run('trash-list', *args)
    def run(self,*argv):
        file_reader = FileSystemReader()
        file_reader.list_volumes = lambda: self.volumes
        ListCmd(
            out         = self.stdout,
            err         = self.stderr,
            environ     = self.environ,
            getuid      = self.fake_getuid,
            file_reader = file_reader,
            list_volumes = lambda: self.volumes,
        ).run(*argv)
    def set_fake_uid(self, uid):
        self.fake_getuid = lambda: uid
    def add_volume(self, mount_point):
        self.volumes.append(mount_point)
    def error(self):
        return self.stderr.getvalue()
    def output(self):
        return self.stdout.getvalue()

