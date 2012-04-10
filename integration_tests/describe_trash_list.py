# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

import os
from trashcli.trash import ListCmd
from files import (write_file, require_empty_dir, make_sticky_dir,
                   ensure_non_sticky_dir, make_unsticky_dir,
                   make_unreadable_file, make_empty_file, make_parent_for)
from nose.tools import istest
from .output_collector import OutputCollector
from trashinfo import (
        a_trashinfo,
        a_trashinfo_without_date,
        a_trashinfo_without_path,
        a_trashinfo_with_invalid_date)
from textwrap import dedent

class Setup(object):
    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')
        require_empty_dir('topdir')

        self.user = TrashListUser(
                environ = {'XDG_DATA_HOME': 'XDG_DATA_HOME'})

        self.home_trashcan = FakeTrashDir('XDG_DATA_HOME/Trash')
        self.add_trashinfo = self.home_trashcan.add_trashinfo
    def when_dir_is_sticky(self, path):
        make_sticky_dir(path)
    def when_dir_exists_unsticky(self, path):
        make_unsticky_dir(path)


@istest
class describe_trash_list(Setup):

    @istest
    def should_output_the_help_message(self):

        self.user.run('trash-list', '--help')

        self.user.should_read_output(dedent("""\
            Usage: trash-list [OPTIONS...]

            List trashed files

            Options:
              --version   show program's version number and exit
              -h, --help  show this help message and exit

            Report bugs to http://code.google.com/p/trash-cli/issues
        """))

    @istest
    def should_output_nothing_when_trashcan_is_empty(self):

        self.user.run_trash_list()

        self.user.should_read_output('')

    @istest
    def should_output_deletion_date_and_path(self):
        self.add_trashinfo('/aboslute/path', '2001-02-03T23:55:59')

        self.user.run_trash_list()

        self.user.should_read_output( "2001-02-03 23:55:59 /aboslute/path\n")

    @istest
    def should_output_info_for_multiple_files(self):
        self.add_trashinfo("/file1", "2000-01-01T00:00:01")
        self.add_trashinfo("/file2", "2000-01-01T00:00:02")
        self.add_trashinfo("/file3", "2000-01-01T00:00:03")

        self.user.run_trash_list()

        self.user.should_read_output( "2000-01-01 00:00:01 /file1\n"
                                      "2000-01-01 00:00:02 /file2\n"
                                      "2000-01-01 00:00:03 /file3\n")

    @istest
    def should_output_unknown_dates_with_question_marks(self):

        self.home_trashcan.having_file(a_trashinfo_without_date())

        self.user.run_trash_list()

        self.user.should_read_output("????-??-?? ??:??:?? /path\n")

    @istest
    def should_output_invalid_dates_using_question_marks(self):
        self.home_trashcan.having_file(a_trashinfo_with_invalid_date())

        self.user.run_trash_list()

        self.user.should_read_output("????-??-?? ??:??:?? /path\n")

    @istest
    def should_warn_about_empty_trashinfos(self):
        self.home_trashcan.touch('empty.trashinfo')

        self.user.run_trash_list()

        self.user.should_read_error(
                "Parse Error: XDG_DATA_HOME/Trash/info/empty.trashinfo: "
                "Unable to parse Path.\n")

    @istest
    def should_warn_about_unreadable_trashinfo(self):
        self.home_trashcan.having_unreadable('unreadable.trashinfo')

        self.user.run_trash_list()

        self.user.should_read_error(
                "[Errno 13] Permission denied: "
                "'XDG_DATA_HOME/Trash/info/unreadable.trashinfo'\n")
    @istest
    def should_warn_about_unexistent_path_entry(self):
        self.home_trashcan.having_file(a_trashinfo_without_path())

        self.user.run_trash_list()

        self.user.should_read_error(
                "Parse Error: XDG_DATA_HOME/Trash/info/1.trashinfo: "
                "Unable to parse Path.\n")
        self.user.should_read_output('')

@istest
class with_a_top_trash_dir(Setup):
    def setUp(self):
        super(type(self),self).setUp()
        self.top_trashdir1 = FakeTrashDir('topdir/.Trash/123')
        self.user.set_fake_uid(123)
        self.user.add_volume('topdir')

    @istest
    def should_list_its_contents_if_parent_is_sticky(self):
        self.when_dir_is_sticky('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        self.user.should_read_output("2000-01-01 00:00:00 topdir/file1\n")
    
    @istest
    def and_should_warn_if_parent_is_not_sticky(self):
        self.when_dir_exists_unsticky('topdir/.Trash')
        self.and_dir_exists('topdir/.Trash/123')

        self.user.run_trash_list()

        self.user.should_read_error("TrashDir skipped because parent not sticky: topdir/.Trash/123\n")

    @istest
    def but_it_should_not_warn_when_the_parent_is_unsticky_but_there_is_no_trashdir(self):
        self.when_dir_exists_unsticky('topdir/.Trash')
        self.but_does_not_exists_any('topdir/.Trash/123')

        self.user.run_trash_list()

        self.user.should_read_error("")

    @istest
    def should_ignore_trash_from_a_unsticky_topdir(self):
        self.when_dir_exists_unsticky('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        self.user.should_read_output("")

    @istest
    def it_should_ignore_Trash_is_a_symlink(self):
        self.when_is_a_symlink_to_a_dir('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        self.user.should_read_output('')

    @istest
    def and_should_warn_about_it(self):
        self.when_is_a_symlink_to_a_dir('topdir/.Trash')
        self.and_contains_a_valid_trashinfo()

        self.user.run_trash_list()

        self.user.should_read_error('TrashDir skipped because parent not sticky: topdir/.Trash/123\n')
    def but_does_not_exists_any(self, path):
        assert not os.path.exists(path)
    def and_dir_exists(self, path):
        os.mkdir(path)
        assert os.path.isdir(path)
    def and_contains_a_valid_trashinfo(self):
        self.top_trashdir1.add_trashinfo('file1', '2000-01-01T00:00:00')
    def when_is_a_symlink_to_a_dir(self, path):
        dest = "%s-dest" % path
        os.mkdir(dest)
        rel_dest = os.path.basename(dest)
        os.symlink(rel_dest, path)

@istest
class describe_when_a_file_is_in_alternate_top_trashdir(Setup):
    @istest
    def should_list_contents_of_alternate_trashdir(self):
        self.user.set_fake_uid(123)
        self.user.add_volume('topdir')
        self.top_trashdir2 = FakeTrashDir('topdir/.Trash-123')
        self.top_trashdir2.add_trashinfo('file', '2000-01-01T00:00:00')

        self.user.run_trash_list()

        self.user.should_read_output("2000-01-01 00:00:00 topdir/file\n")

from nose.tools import assert_raises

@istest
class describe_trash_list_with_raw_option:
    def setup(self):
        self.having_XDG_DATA_HOME('XDG_DATA_HOME')
        self.running('trash-list', '--raw')
    @istest
    def output_should_contains_trashinfo_paths(self):
        from nose import SkipTest; raise SkipTest()
        self.having_trashinfo('foo.trashinfo')
        self.output_should_contain_line(
            'XDG_DATA_HOME/Trash/info/foo.trashinfo')
    @istest
    def output_should_contains_backup_copy_paths(self):
        from nose import SkipTest; raise SkipTest()
        self.having_trashinfo('foo.trashinfo')
        self.output_should_contain_line(
            'XDG_DATA_HOME/Trash/files/foo')

    def having_XDG_DATA_HOME(self, value):
        self.XDG_DATA_HOME = value
    def running(self, *argv):
        user = TrashListUser( environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME})
        user.run(argv)
        self.output = user.output()
    def output_should_contain_line(self, line):
        assert line in self.output_lines()
    def output_lines(self):
        return [line.rstrip('\n') for line in self.output.splitlines()]


class FakeTrashDir:
    def __init__(self, path):
        self.path = path + '/info'
        self.number = 1
    def touch(self, path_relative_to_info_dir):
        make_empty_file(self.join(path_relative_to_info_dir))
    def having_unreadable(self, path_relative_to_info_dir):
        path = self.join(path_relative_to_info_dir)
        make_unreadable_file(path)
    def join(self, path_relative_to_info_dir):
        import os
        return os.path.join(self.path, path_relative_to_info_dir)
    def having_file(self, contents):
        path = '%(info_dir)s/%(name)s.trashinfo' % { 'info_dir' : self.path,
                                                     'name'     : str(self.number)}
        make_parent_for(path)
        write_file(path, contents)

        self.number += 1
        self.path_of_last_file_added = path

    def add_trashinfo(self, escaped_path_entry, formatted_deletion_date):
        self.having_file(a_trashinfo(escaped_path_entry, formatted_deletion_date))

class TrashListUser:
    def __init__(self, environ={}):
        self.stdout      = OutputCollector()
        self.stderr      = OutputCollector()
        self.environ     = environ
        self.fake_getuid = self.error
        self.volumes     = []
    def run_trash_list(self):
        self.run('trash-list')
    def run(self,*argv):
        from trashcli.trash import FileSystemReader
        file_reader = FileSystemReader()
        file_reader.list_volumes = lambda: self.volumes
        ListCmd(
            out         = self.stdout,
            err         = self.stderr,
            environ     = self.environ,
            getuid      = self.fake_getuid,
            file_reader = file_reader,
        ).run(*argv)
    def set_fake_uid(self, uid):
        self.fake_getuid = lambda: uid
    def add_volume(self, mount_point):
        self.volumes.append(mount_point)
    def error(self):
        raise ValueError()
    def should_read_output(self, expected_value):
        self.stdout.assert_equal_to(expected_value)
    def should_read_error(self, expected_value):
        self.stderr.assert_equal_to(expected_value)
    def output(self):
        return self.stdout.getvalue()

