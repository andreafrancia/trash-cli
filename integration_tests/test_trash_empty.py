# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals, assert_items_equal, istest
from trashcli.trash import EmptyCmd

from StringIO import StringIO
import os
from files import write_file, require_empty_dir, make_dirs, set_sticky_bit
from files import having_file
from mock import MagicMock

@istest
class describe_trash_empty:

    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')
        self.info_dir_path   = 'XDG_DATA_HOME/Trash/info'
        self.files_dir_path  = 'XDG_DATA_HOME/Trash/files'
        self.environ = {'XDG_DATA_HOME':'XDG_DATA_HOME'}
        now = MagicMock(side_effect=RuntimeError)
        self.empty_cmd = EmptyCmd(
            out = StringIO(),
            err = StringIO(),
            environ = self.environ,
            now = now
        )

    def user_run_trash_empty(self):
        self.empty_cmd.run('trash-empty')

    @istest
    def it_should_remove_an_info_file(self):
        self.having_a_trashinfo_in_trashcan('foo.trashinfo')

        self.user_run_trash_empty()

        self.assert_dir_empty(self.info_dir_path)

    @istest
    def it_should_remove_all_the_infofiles(self):
        self.having_three_trashinfo_in_trashcan()

        self.user_run_trash_empty()

        self.assert_dir_empty(self.info_dir_path)

    @istest
    def it_should_remove_the_backup_files(self):
        self.having_one_trashed_file()

        self.user_run_trash_empty()

        self.assert_dir_empty(self.files_dir_path)

    @istest
    def it_should_keep_unknown_files_found_in_infodir(self):
        self.having_file_in_info_dir('not-a-trashinfo')

        self.user_run_trash_empty()

        self.assert_dir_contains(self.info_dir_path, 'not-a-trashinfo')

    @istest
    def but_it_should_remove_orphan_files_from_the_files_dir(self):
        self.having_orphan_file_in_files_dir()

        self.user_run_trash_empty()

        self.assert_dir_empty(self.files_dir_path)

    @istest
    def it_should_purge_also_directories(self):
        os.makedirs("XDG_DATA_HOME/Trash/files/a-dir")

        self.user_run_trash_empty()

    def assert_dir_empty(self, path):
        assert len(os.listdir(path)) == 0

    def assert_dir_contains(self, path, filename):
        assert os.path.exists(os.path.join(path, filename))

    def having_a_trashinfo_in_trashcan(self, basename_of_trashinfo):
        having_file(os.path.join(self.info_dir_path, basename_of_trashinfo))

    def having_three_trashinfo_in_trashcan(self):
        self.having_a_trashinfo_in_trashcan('foo.trashinfo')
        self.having_a_trashinfo_in_trashcan('bar.trashinfo')
        self.having_a_trashinfo_in_trashcan('baz.trashinfo')
        assert_items_equal(['foo.trashinfo',
                            'bar.trashinfo',
                            'baz.trashinfo'], os.listdir(self.info_dir_path))

    def having_one_trashed_file(self):
        self.having_a_trashinfo_in_trashcan('foo.trashinfo')
        having_file(self.files_dir_path +'/foo')
        self.files_dir_should_not_be_empty()

    def files_dir_should_not_be_empty(self):
        assert len(os.listdir(self.files_dir_path)) != 0

    def having_file_in_info_dir(self, filename):
        having_file(os.path.join(self.info_dir_path, filename))

    def having_orphan_file_in_files_dir(self):
        complete_path = os.path.join(self.files_dir_path,
                                     'a-file-without-any-associated-trashinfo')
        having_file(complete_path)
        assert os.path.exists(complete_path)

@istest
class describe_trash_empty_invoked_with_N_days_as_argument:
    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')
        self.xdg_data_home   = 'XDG_DATA_HOME'
        self.environ = {'XDG_DATA_HOME':'XDG_DATA_HOME'}
        self.now = MagicMock(side_effect=RuntimeError)
        self.empty_cmd=EmptyCmd(
            out = StringIO(),
            err = StringIO(),
            environ = self.environ,
            now = self.now
        )

    def user_run_trash_empty(self, *args):
        self.empty_cmd.run('trash-empty', *args)

    def set_clock_at(self, yyyy_mm_dd):
        self.now.side_effect = lambda:date(yyyy_mm_dd)

        def date(yyyy_mm_dd):
            from datetime import datetime
            return datetime.strptime(yyyy_mm_dd, '%Y-%m-%d')

    @istest
    def it_should_keep_files_newer_than_N_days(self):
        self.having_a_trashed_file('foo', '2000-01-01')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    @istest
    def it_should_remove_files_older_than_N_days(self):
        self.having_a_trashed_file('foo', '1999-01-01')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_removed_from_trashcan('foo')

    @istest
    def it_should_kept_files_with_invalid_deletion_date(self):
        self.having_a_trashed_file('foo', 'Invalid Date')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    def having_a_trashed_file(self, name, date):
        contents = "DeletionDate=%sT00:00:00\n" % date
        write_file(self.trashinfo(name), contents)

    def trashinfo(self, name):
        return '%(dirname)s/Trash/info/%(name)s.trashinfo' % {
                    'dirname' : self.xdg_data_home,
                    'name'    : name }

    def file_should_have_been_kept_in_trashcan(self, trashinfo_name):
        assert os.path.exists(self.trashinfo(trashinfo_name))
    def file_should_have_been_removed_from_trashcan(self, trashinfo_name):
        assert not os.path.exists(self.trashinfo(trashinfo_name))

class TestEmptyCmdWithMultipleVolumes:
    def setUp(self):
        require_empty_dir('topdir')
        self.empty=EmptyCmd(
                out          = StringIO(),
                err          = StringIO(),
                environ      = {},
                getuid       = lambda: 123,
                list_volumes = lambda: ['topdir'],)

    def test_it_removes_trashinfos_from_method_1_dir(self):
        self.make_proper_top_trash_dir('topdir/.Trash')
        having_file('topdir/.Trash/123/info/foo.trashinfo')

        self.empty.run('trash-empty')

        assert not os.path.exists('topdir/.Trash/123/info/foo.trashinfo')
    def test_it_removes_trashinfos_from_method_2_dir(self):
        having_file('topdir/.Trash-123/info/foo.trashinfo')

        self.empty.run('trash-empty')

        assert not os.path.exists('topdir/.Trash-123/info/foo.trashinfo')

    def make_proper_top_trash_dir(self, path):
        make_dirs(path)
        set_sticky_bit(path)

from textwrap import dedent
class TestTrashEmpty_on_help:
    def test_help_output(self):
        err, out = StringIO(), StringIO()
        cmd = EmptyCmd(err = err,
                       out = out,
                       environ = {},)
        cmd.run('trash-empty', '--help')
        assert_equals(out.getvalue(), dedent("""\
            Usage: trash-empty [days]

            Purge trashed files.

            Options:
              --version   show program's version number and exit
              -h, --help  show this help message and exit

            Report bugs to http://code.google.com/p/trash-cli/issues
            """))

class TestTrashEmpty_on_version():
    def test_it_print_version(self):
        err, out = StringIO(), StringIO()
        cmd = EmptyCmd(err = err,
                       out = out,
                       environ = {},
                       version = '1.2.3')
        cmd.run('trash-empty', '--version')
        assert_equals(out.getvalue(), dedent("""\
            trash-empty 1.2.3
            """))

