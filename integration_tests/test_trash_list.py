# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import ListCmd
from files import (write_file, require_empty_dir, make_sticky_dir,
                   ensure_non_sticky_dir, make_unreadable_file,
                   make_empty_file)
from nose.tools import istest
from .output_collector import OutputCollector
from trashinfo import (a_trashinfo, a_trashinfo_without_date,
                       a_trashinfo_with_invalid_date)

@istest
class Describe_trash_list_output:
    @istest
    def should_output_the_help_message(self):
        self.run('trash-list', '--help')
        self.output_should_be("""\
Usage: trash-list [OPTIONS...]

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""")

    @istest
    def should_output_nothing_if_no_files(self):

        self.run()
        self.output_should_be('')

    @istest
    def should_output_deletion_date_and_path_of_trash(self):

        self.add_trashinfo('/aboslute/path', '2001-02-03T23:55:59')
        self.run()
        self.output_should_be( "2001-02-03 23:55:59 /aboslute/path\n")

    @istest
    def should_works_also_with_multiple_files(self):
        self.add_trashinfo("/file1", "2000-01-01T00:00:01")
        self.add_trashinfo("/file2", "2000-01-01T00:00:02")
        self.add_trashinfo("/file3", "2000-01-01T00:00:03")

        self.run()

        self.output_should_be( "2000-01-01 00:00:01 /file1\n"
                                  "2000-01-01 00:00:02 /file2\n"
                                  "2000-01-01 00:00:03 /file3\n")

    @istest
    def should_output_question_mark_if_deletion_date_is_not_present(self):
        self.info_dir.having_file(a_trashinfo_without_date())
        self.run()
        self.output_should_be("????-??-?? ??:??:?? /path\n")

    @istest
    def should_output_question_marks_if_deletion_date_is_invalid(self):
        self.info_dir.having_file(a_trashinfo_with_invalid_date())
        self.run()
        self.output_should_be("????-??-?? ??:??:?? /path\n")

    @istest
    def should_warn_about_empty_trashinfos(self):
        self.info_dir.touch('empty.trashinfo')
        self.run()
        self.error_should_be(
                "Parse Error: XDG_DATA_HOME/Trash/info/empty.trashinfo: "
                "Unable to parse Path\n")

    @istest
    def should_warn_about_unreadable_trashinfo(self):
        self.info_dir.having_unreadable('unreadable.trashinfo')

        self.run()

        self.error_should_be(
                "[Errno 13] Permission denied: "
                "'XDG_DATA_HOME/Trash/info/unreadable.trashinfo'\n")
    @istest
    def should_warn_about_unexistent_path_entry(self):
        def a_trashinfo_without_path():
            return ("[TrashInfo]\n"
                    "DeletionDate='2000-01-01T00:00:00'\n")
        self.info_dir.having_file(a_trashinfo_without_path())

        self.run()

        self.error_should_be(
                "Parse Error: XDG_DATA_HOME/Trash/info/1.trashinfo: "
                "Unable to parse Path\n")
        self.output_should_be('')

    def setUp(self):
        self.XDG_DATA_HOME = 'XDG_DATA_HOME'
        require_empty_dir( self.XDG_DATA_HOME)

        self.info_dir      = FakeInfoDir(self.XDG_DATA_HOME+'/Trash/info')
        self.add_trashinfo = self.info_dir.add_trashinfo

        runner = TrashListRunner( environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME})
        self.output_should_be = runner.output_should_be
        self.error_should_be  = runner.error_should_be
        self.run = runner

@istest
class describe_list_trash_with_top_trash_directory_type_1:
    @istest
    def should_list_method_1_trashcan_contents(self):
        make_sticky_dir('topdir/.Trash')
        trashdir = FakeInfoDir('topdir/.Trash/123/info')
        trashdir.add_trashinfo('file1', '2000-01-01T00:00:00')

        self.run()

        self.output_should_be("2000-01-01 00:00:00 topdir/file1\n")

    @istest
    def should_ignore_contents_when_is_not_sticky(self):
        trashdir = FakeInfoDir('topdir/.Trash/123/info')
        trashdir.add_trashinfo('file1', '2000-01-01T00:00:00')
        ensure_non_sticky_dir('topdir/.Trash')

        self.run()

        self.output_should_be("")

    @istest
    def should_list_method2_trashcan_contents(self):
        trashdir = FakeInfoDir('topdir/.Trash-123/info')
        trashdir.add_trashinfo('file', '2000-01-01T00:00:00')

        self.run()

        self.output_should_be("2000-01-01 00:00:00 topdir/file\n")

    def setUp(self):
        require_empty_dir('topdir')

        runner = TrashListRunner()
        runner.set_fake_uid(123)
        runner.add_volume('topdir')

        self.run = runner
        self.output_should_be = runner.output_should_be

class FakeInfoDir:
    def __init__(self, path):
        self.path = path
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
        write_file(path, contents)

        self.number += 1
        self.path_of_last_file_added = path

    def add_trashinfo(self, escaped_path_entry, formatted_deletion_date):
        self.having_file(a_trashinfo(escaped_path_entry, formatted_deletion_date))

class TrashListRunner:
    def __init__(self, environ={}):
        self.stdout      = OutputCollector()
        self.stderr      = OutputCollector()
        self.environ     = environ
        self.fake_getuid = self.error
        self.volumes     = []
    def __call__(self, *argv):
        self.run(argv)
    def run(self,argv):
        if argv==(): 
            argv='trash-list'
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
    def output_should_be(self, expected_value):
        self.stdout.assert_equal_to(expected_value)
    def error_should_be(self, expected_value):
        self.stderr.assert_equal_to(expected_value)

