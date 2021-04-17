# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import unittest

from trashcli.empty import EmptyCmd

from unit_tests.myStringIO import StringIO
import os

from .empty import no_volumes
from .files import make_file, require_empty_dir, make_dirs, set_sticky_bit, \
    make_unreadable_dir, make_empty_file, make_readable
from unit_tests.support import MyPath
from mock import MagicMock
from trashcli.fs import FileSystemReader
from trashcli.fs import FileRemover
import six

from trashcli.empty import main as empty


class TestEmptyCmd_with_help(unittest.TestCase):
    def test(self):
        out = StringIO()
        empty(['trash-empty', '-h'], stdout = out)
        six.assertRegex(self, out.getvalue(), '^Usage. trash-empty.*')


class TestTrashEmptyCmd(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.unreadable_dir = self.tmp_dir / 'data/Trash/files/unreadable'

    def test_trash_empty_will_skip_unreadable_dir(self):
        out = StringIO()
        err = StringIO()

        make_unreadable_dir(self.unreadable_dir)

        empty(['trash-empty'], stdout = out, stderr = err,
                environ={'XDG_DATA_HOME':self.tmp_dir / 'data'})

        assert ("trash-empty: cannot remove %s\n"  % self.unreadable_dir ==
                     err.getvalue())

    def tearDown(self):
        make_readable(self.unreadable_dir)
        self.tmp_dir.clean_up()


class TestWhen_invoked_with_N_days_as_argument(unittest.TestCase):
    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')
        self.xdg_data_home   = 'XDG_DATA_HOME'
        self.environ = {'XDG_DATA_HOME':'XDG_DATA_HOME'}
        self.now = MagicMock(side_effect=RuntimeError)
        self.empty_cmd=EmptyCmd(
            out = StringIO(),
            err = StringIO(),
            environ = self.environ,
            list_volumes = no_volumes,
            now = self.now,
            file_reader = FileSystemReader(),
            getuid = None,
            file_remover = FileRemover(),
            version = None,
        )

    def user_run_trash_empty(self, *args):
        self.empty_cmd.run('trash-empty', *args)

    def set_clock_at(self, yyyy_mm_dd):
        self.now.side_effect = lambda:date(yyyy_mm_dd)

        def date(yyyy_mm_dd):
            from datetime import datetime
            return datetime.strptime(yyyy_mm_dd, '%Y-%m-%d')

    def test_it_should_keep_files_newer_than_N_days(self):
        self.having_a_trashed_file('foo', '2000-01-01')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    def test_it_should_remove_files_older_than_N_days(self):
        self.having_a_trashed_file('foo', '1999-01-01')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_removed_from_trashcan('foo')

    def test_it_should_kept_files_with_invalid_deletion_date(self):
        self.having_a_trashed_file('foo', 'Invalid Date')
        self.set_clock_at('2000-01-01')

        self.user_run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    def having_a_trashed_file(self, name, date):
        contents = "DeletionDate=%sT00:00:00\n" % date
        make_file(self.trashinfo(name), contents)

    def trashinfo(self, name):
        return '%(dirname)s/Trash/info/%(name)s.trashinfo' % {
                    'dirname' : self.xdg_data_home,
                    'name'    : name }

    def file_should_have_been_kept_in_trashcan(self, trashinfo_name):
        assert os.path.exists(self.trashinfo(trashinfo_name))
    def file_should_have_been_removed_from_trashcan(self, trashinfo_name):
        assert not os.path.exists(self.trashinfo(trashinfo_name))


class TestEmptyCmdWithMultipleVolumes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.top_dir = self.temp_dir / 'topdir'
        require_empty_dir(self.top_dir)
        self.empty=EmptyCmd(
                out          = StringIO(),
                err          = StringIO(),
                environ      = {},
                list_volumes = lambda: [self.top_dir],
                now          = None,
                file_reader  = FileSystemReader(),
                getuid       = lambda: 123,
                file_remover = FileRemover(),
                version      = None,
        )

    def test_it_removes_trashinfos_from_method_1_dir(self):
        self.make_proper_top_trash_dir(self.top_dir / '.Trash')
        make_empty_file(self.top_dir / '.Trash/123/info/foo.trashinfo')

        self.empty.run('trash-empty')

        assert not os.path.exists(
            self.top_dir / '.Trash/123/info/foo.trashinfo')
    def test_it_removes_trashinfos_from_method_2_dir(self):
        make_empty_file(self.top_dir / '.Trash-123/info/foo.trashinfo')

        self.empty.run('trash-empty')

        assert not os.path.exists(
            self.top_dir / '.Trash-123/info/foo.trashinfo')

    def test_it_removes_trashinfo_from_specified_trash_dir(self):
        make_empty_file(self.temp_dir / 'specified/info/foo.trashinfo')

        self.empty.run('trash-empty', '--trash-dir',
                       self.temp_dir / 'specified')

        assert not os.path.exists(
            self.temp_dir / 'specified/info/foo.trashinfo')


    def make_proper_top_trash_dir(self, path):
        make_dirs(path)
        set_sticky_bit(path)

    def tearDown(self):
        self.temp_dir.clean_up()

from textwrap import dedent
class TestTrashEmpty_on_help(unittest.TestCase):
    def test_help_output(self):
        err, out = StringIO(), StringIO()
        cmd = EmptyCmd(err = err,
                       out = out,
                       environ = {},
                       list_volumes = no_volumes,
                       now = None,
                       file_reader = FileSystemReader(),
                       getuid = None,
                       file_remover = None,
                       version = None,
                       )
        cmd.run('trash-empty', '--help')
        assert out.getvalue() == dedent("""\
            Usage: trash-empty [days]

            Purge trashed files.

            Options:
              --version   show program's version number and exit
              -h, --help  show this help message and exit

            Report bugs to https://github.com/andreafrancia/trash-cli/issues
            """)

class TestTrashEmpty_on_version(unittest.TestCase):
    def test_it_print_version(self):
        err, out = StringIO(), StringIO()
        cmd = EmptyCmd(err = err,
                       out = out,
                       environ = {},
                       list_volumes = no_volumes,
                       now = None,
                       file_reader = FileSystemReader(),
                       getuid = None,
                       file_remover = None,
                       version = '1.2.3',
                       )
        cmd.run('trash-empty', '--version')
        assert out.getvalue() == dedent("""\
            trash-empty 1.2.3
            """)


class Test_describe_trash_empty_command_line__on_invalid_options(unittest.TestCase):
    def setUp(self):
        self.err, self.out = StringIO(), StringIO()
        self.cmd = EmptyCmd(
                       err = self.err,
                       out = self.out,
                       environ = {},
                       list_volumes = no_volumes,
                       now = None,
                       file_reader = FileSystemReader(),
                       getuid = None,
                       file_remover = None,
                       version = None,
                       )

    def test_it_should_fail(self):

        self.exit_code = self.cmd.run('trash-empty', '-2')

        exit_code_for_command_line_usage = 64
        assert exit_code_for_command_line_usage == self.exit_code

    def test_it_should_complain_to_the_standard_error(self):

        self.exit_code = self.cmd.run('trash-empty', '-2')

        assert self.err.getvalue() == dedent("""\
                trash-empty: invalid option -- '2'
                """)

    def test_with_a_different_option(self):

        self.cmd.run('trash-empty', '-3')

        assert self.err.getvalue() == dedent("""\
                trash-empty: invalid option -- '3'
                """)
