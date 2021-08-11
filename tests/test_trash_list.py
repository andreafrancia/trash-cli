# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
from datetime import datetime
import os

import pytest

from trashcli import trash
from trashcli.fstab import VolumesListing
from mock import Mock

from trashcli.list import ListCmd
from .files import (require_empty_dir, make_sticky_dir, make_unsticky_dir)
from .support import MyPath
from .output_collector import OutputCollector
from .fake_trash_dir import FakeTrashDir
from trashcli.fs import FileSystemReader
from .asserts import assert_equals_with_unidiff
import unittest


@pytest.mark.slow
class Setup(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.xdg_data_home = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / "topdir"
        require_empty_dir(self.top_dir)
        self.user = TrashListUser(self.xdg_data_home)

    def tearDown(self):
        self.xdg_data_home.clean_up()
        self.temp_dir.clean_up()


def sort_lines(lines):
    return "".join(sorted(lines.splitlines(True)))

class Test_describe_trash_list(Setup):

    def test_should_output_the_version(self):

        self.user.run_trash_list('--version')

        assert_equals_with_unidiff('trash-list %s\n' % trash.version,
                                   self.user.output())

    def test_should_output_nothing_when_trashcan_is_empty(self):

        self.user.run_trash_list()

        assert_equals_with_unidiff('', self.user.output())

    def test_should_output_deletion_date_and_path(self):
        self.user.home_trashdir.add_trashinfo2('/aboslute/path',
                                               datetime(2001,2,3,23,55,59))

        self.user.run_trash_list()

        assert_equals_with_unidiff("2001-02-03 23:55:59 /aboslute/path\n",
                                   self.user.output())

    def test_should_output_info_for_multiple_files(self):
        self.user.home_trashdir.add_trashinfo2("/file1", datetime(2000,1,1,0,0,1))
        self.user.home_trashdir.add_trashinfo2("/file2", datetime(2000,1,1,0,0,2))
        self.user.home_trashdir.add_trashinfo2("/file3", datetime(2000,1,1,0,0,3))

        self.user.run_trash_list()
        output = self.user.output()

        assert_equals_with_unidiff("2000-01-01 00:00:01 /file1\n"
                                   "2000-01-01 00:00:02 /file2\n"
                                   "2000-01-01 00:00:03 /file3\n",
                                   sort_lines(output))

    def test_should_output_unknown_dates_with_question_marks(self):
        self.user.home_trashdir.add_trashinfo_without_date('without-date')

        self.user.run_trash_list()

        assert self.user.output() == "????-??-?? ??:??:?? /without-date\n"


    def test_should_output_invalid_dates_using_question_marks(self):
        self.user.home_trashdir.add_trashinfo_wrong_date('with-invalid-date',
                                                         'Wrong date')

        self.user.run_trash_list()

        assert_equals_with_unidiff("????-??-?? ??:??:?? /with-invalid-date\n",
                                   self.user.output())

    def test_should_warn_about_empty_trashinfos(self):
        self.user.home_trashdir.add_trashinfo_content('empty', '')

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
        self.user.home_trashdir.add_trashinfo_without_path("foo")

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "Parse Error: %(XDG_DATA_HOME)s/Trash/info/foo.trashinfo: "
            "Unable to parse Path.\n" % {
                'XDG_DATA_HOME': self.xdg_data_home},
            self.user.error())
        assert_equals_with_unidiff('', self.user.output())

class Test_with_a_top_trash_dir(Setup):
    def setUp(self):
        super(type(self),self).setUp()
        self.top_trashdir1 = FakeTrashDir(self.top_dir / '.Trash/123')
        self.user.set_fake_uid(123)
        self.user.add_volume(self.top_dir)

    def test_should_list_its_contents_if_parent_is_sticky(self):
        make_sticky_dir(self.top_dir / '.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff("2000-01-01 00:00:00 %s/file1\n" % self.top_dir,
                                   self.user.output())

    def test_and_should_warn_if_parent_is_not_sticky(self):
        make_unsticky_dir(self.top_dir / '.Trash')
        self.and_dir_exists(self.top_dir / '.Trash/123')

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            "TrashDir skipped because parent not sticky: %s/.Trash/123\n" %
            self.top_dir,
            self.user.error()
        )

    def test_but_it_should_not_warn_when_the_parent_is_unsticky_but_there_is_no_trashdir(self):
        make_unsticky_dir(self.top_dir / '.Trash')
        self.but_does_not_exists_any(self.top_dir / '.Trash/123')

        self.user.run_trash_list()

        assert_equals_with_unidiff("", self.user.error())

    def test_should_ignore_trash_from_a_unsticky_topdir(self):
        make_unsticky_dir(self.top_dir / '.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff('', self.user.output())

    def test_it_should_ignore_Trash_is_a_symlink(self):
        self.when_is_a_symlink_to_a_dir(self.top_dir / '.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff('', self.user.output())

    def test_and_should_warn_about_it(self):
        self.when_is_a_symlink_to_a_dir(self.top_dir / '.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        assert_equals_with_unidiff(
            'TrashDir skipped because parent not sticky: %s/.Trash/123\n' %
            self.top_dir,
            self.user.error()
        )

    def but_does_not_exists_any(self, path):
        assert not os.path.exists(path)
    def and_dir_exists(self, path):
        os.mkdir(path)
        assert os.path.isdir(path)

    def and_contains_a_valid_trashinfo(self):
        self.top_trashdir1.add_trashinfo2('file1', datetime(2000,1,1,0,0,0))

    def when_is_a_symlink_to_a_dir(self, path):
        dest = "%s-dest" % path
        os.mkdir(dest)
        rel_dest = os.path.basename(dest)
        os.symlink(rel_dest, path)


class Test_describe_when_a_file_is_in_alternate_top_trashdir(Setup):

    def test_should_list_contents_of_alternate_trashdir(self):
        self.user.set_fake_uid(123)
        self.user.add_volume(self.top_dir)
        self.top_trashdir2 = FakeTrashDir(self.top_dir / '.Trash-123')
        self.top_trashdir2.add_trashinfo2('file', datetime(2000,1,1,0,0,0))

        self.user.run_trash_list()

        assert_equals_with_unidiff("2000-01-01 00:00:00 %s/file\n" %
                                   self.top_dir,
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
        volumes_listing = Mock(spec=VolumesListing)
        volumes_listing.list_volumes.return_value =  self.volumes
        ListCmd(
            out         = self.stdout,
            err         = self.stderr,
            environ     = self.environ,
            getuid      = self.fake_getuid,
            file_reader = file_reader,
            volumes_listing=volumes_listing,
        ).run(*argv)
    def set_fake_uid(self, uid):
        self.fake_getuid = lambda: uid
    def add_volume(self, mount_point):
        self.volumes.append(mount_point)
    def error(self):
        return self.stderr.getvalue()
    def output(self):
        return self.stdout.getvalue()

