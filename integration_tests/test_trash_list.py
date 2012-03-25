# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import ListCmd
from files import (write_file, require_empty_dir, make_sticky_dir,
                   ensure_non_sticky_dir, make_unreadable_file,
                   make_empty_file, make_parent_for)
from nose.tools import istest
from .output_collector import OutputCollector
from trashinfo import (
        a_trashinfo,
        a_trashinfo_without_date,
        a_trashinfo_without_path,
        a_trashinfo_with_invalid_date)

@istest
class describe_trash_list_output:
    @istest
    def should_output_the_help_message(self):
        self.user.run('trash-list', '--help')
        self.user.should_read_output("""\
Usage: trash-list [OPTIONS...]

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""")

    @istest
    def should_output_nothing_if_no_files(self):

        self.user.run_trash_list()
        self.user.should_read_output('')

    @istest
    def should_output_deletion_date_and_path_of_trash(self):

        self.add_trashinfo('/aboslute/path', '2001-02-03T23:55:59')
        self.user.run_trash_list()
        self.user.should_read_output( "2001-02-03 23:55:59 /aboslute/path\n")

    @istest
    def should_works_also_with_multiple_files(self):
        self.add_trashinfo("/file1", "2000-01-01T00:00:01")
        self.add_trashinfo("/file2", "2000-01-01T00:00:02")
        self.add_trashinfo("/file3", "2000-01-01T00:00:03")

        self.user.run_trash_list()

        self.user.should_read_output( "2000-01-01 00:00:01 /file1\n"
                                      "2000-01-01 00:00:02 /file2\n"
                                      "2000-01-01 00:00:03 /file3\n")

    @istest
    def should_output_question_mark_if_deletion_date_is_not_present(self):
        self.home_trashcan.having_file(a_trashinfo_without_date())
        self.user.run_trash_list()
        self.user.should_read_output("????-??-?? ??:??:?? /path\n")

    @istest
    def should_output_question_marks_if_deletion_date_is_invalid(self):
        self.home_trashcan.having_file(a_trashinfo_with_invalid_date())
        self.user.run_trash_list()
        self.user.should_read_output("????-??-?? ??:??:?? /path\n")

    @istest
    def should_warn_about_empty_trashinfos(self):
        self.home_trashcan.touch('empty.trashinfo')
        self.user.run_trash_list()
        self.user.should_read_error(
                "Parse Error: XDG_DATA_HOME/Trash/info/empty.trashinfo: "
                "Unable to parse Path\n")

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
                "Unable to parse Path\n")
        self.user.should_read_output('')

    @istest
    def should_list_contebts_of_primary_trashdir(self):
        make_sticky_dir('topdir/.Trash')
        self.top_trashdir1.add_trashinfo('file1', '2000-01-01T00:00:00')

        self.user.run_trash_list()

        self.user.should_read_output("2000-01-01 00:00:00 topdir/file1\n")

    @istest
    def should_ignore_contents_of_non_sticky_trash_dirs(self):
        self.top_trashdir1.add_trashinfo('file1', '2000-01-01T00:00:00')
        ensure_non_sticky_dir('topdir/.Trash')

        self.user.run_trash_list()

        self.user.should_read_output("")

    @istest
    def should_list_contents_of_alternate_trashdir(self):
        self.top_trashdir2.add_trashinfo('file', '2000-01-01T00:00:00')

        self.user.run_trash_list()

        self.user.should_read_output("2000-01-01 00:00:00 topdir/file\n")

    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')
        require_empty_dir('topdir')

        self.user = TrashListUser(
                environ = {'XDG_DATA_HOME': 'XDG_DATA_HOME'})
        self.user.set_fake_uid(123)
        self.user.add_volume('topdir')

        self.home_trashcan = FakeTrashDir('XDG_DATA_HOME/Trash')
        self.top_trashdir1 = FakeTrashDir('topdir/.Trash/123')
        self.top_trashdir2 = FakeTrashDir('topdir/.Trash-123')

        self.add_trashinfo = self.home_trashcan.add_trashinfo

    @istest
    def it_should_not_show_the_contents_when_Trash_is_a_symlink(self):
        make_a_symlink_to_a_dir('topdir/.Trash')
        self.top_trashdir1.add_trashinfo('file1', '2000-01-01T00:00:00')

        self.user.run_trash_list()

        self.user.should_read_output('')

    @istest
    def it_should_notify_when_Trash_is_a_symlink(self):
        make_a_symlink_to_a_dir('topdir/.Trash')

        self.user.run_trash_list()

        with assert_raises(AssertionError):
            self.user.should_read_error('Skipping topdir/.Trash: is a symlink ')

from nose.tools import assert_raises

def make_a_symlink_to_a_dir(path):
    import os
    dest = "%s-dest" % path
    os.mkdir(dest)
    rel_dest = os.path.basename(dest)
    os.symlink(rel_dest, path)

@istest
class describe_trash_list_with_raw_option:
    def setup(self):
        from nose import SkipTest; raise SkipTest()
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
        ListCmd(
            out = self.stdout,
            err = self.stderr,
            environ = self.environ,
            getuid = self.fake_getuid,
            list_volumes = lambda: self.volumes
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

