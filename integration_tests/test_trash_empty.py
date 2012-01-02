# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals, assert_items_equal, istest
from trashcli.trash import EmptyCmd

from StringIO import StringIO
import os
from files import write_file, require_empty_dir, make_dirs, set_sticky_bit
from files import having_file

@istest
class describe_trash_empty:
    @istest
    def it_should_remove_an_info_file(self):
        self.having_a_trashinfo_in_trashcan('foo.trashinfo')

        self.run_trash_empty()

        self.info_dir.should_be_empty()

    @istest
    def it_should_remove_all_the_infofiles(self):

        self.having_three_trashinfo_in_trashcan()

        self.run_trash_empty()

        self.info_dir.should_be_empty()

    @istest
    def it_should_remove_the_backup_files(self):
        self.having_one_trashed_file()

        self.run_trash_empty()

        self.files_dir.should_be_empty()
    
    @istest
    def it_should_keep_unknown_files_found_in_infodir(self):
        self.having_file_in_info_dir('not-a-trashinfo')

        self.run_trash_empty()

        self.info_dir.should_contains_file('not-a-trashinfo')

    @istest
    def but_it_should_remove_orphan_files_from_the_files_dir(self):
        self.having_orphan_file_in_files_dir()

        self.run_trash_empty()

        self.files_dir.should_be_empty()

    def setUp(self):
        class DirChecker:
            def __init__(self, path):
                self.path = path
            def should_be_empty(self):
                assert self.is_empty()
            def is_empty(self):
                return len(os.listdir(self.path)) == 0
            def should_contains_file(self, child):
                assert os.path.exists(os.path.join(self.path, child))
        require_empty_dir('XDG_DATA_HOME')
        self.info_dir_path   = 'XDG_DATA_HOME/Trash/info'
        self.files_dir_path  = 'XDG_DATA_HOME/Trash/files'
        self.info_dir        = DirChecker(self.info_dir_path)
        self.files_dir       = DirChecker(self.files_dir_path)
        self.run_trash_empty = TrashEmptyRunner('XDG_DATA_HOME')
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

    @istest
    def it_should_keep_files_newer_than_N_days(self):

        self.having_a_trashed_file('foo', '2000-01-01')
        self.having_now_is('2000-01-01')

        self.run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    @istest
    def it_should_remove_files_older_than_N_days(self):

        self.having_a_trashed_file('foo', '1999-01-01')
        self.having_now_is('2000-01-01')

        self.run_trash_empty('2')

        self.file_should_have_been_removed_from_trashcan('foo')
        
    @istest
    def it_should_kept_files_with_invalid_deletion_date(self):
        from nose import SkipTest
        raise SkipTest()

        self.having_a_trashed_file('foo', 'Invalid Date')
        self.having_now_is('2000-01-01')
    
        self.run_trash_empty('2')

        self.file_should_have_been_kept_in_trashcan('foo')

    def setUp(self):
        self.xdg_data_home   = 'XDG_DATA_HOME'
        self.run_trash_empty = TrashEmptyRunner(self.xdg_data_home)
        self.having_now_is   = self.run_trash_empty.set_now
        require_empty_dir(self.xdg_data_home)

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

class TrashEmptyRunner:
    def __init__(self, XDG_DATA_HOME):
        self.XDG_DATA_HOME = XDG_DATA_HOME
        self.now = now_not_set
    def __call__(self, *args):
        EmptyCmd(
            out = StringIO(), 
            err = StringIO(), 
            environ = { 'XDG_DATA_HOME': self.XDG_DATA_HOME },
            now = self.now
        ).run('trash-empty', *args)
    def set_now(self, yyyy_mm_dd):
        self.now = lambda: date(yyyy_mm_dd)
def now_not_set(): raise RuntimeError('now_not_set')

class TestEmptyCmdWithMultipleVolumes:
    def test_it_removes_trashinfos_from_method_1_dir(self):
        require_empty_dir('.fake_root')
        make_dirs('.fake_root/media/external-disk/.Trash/')
        set_sticky_bit('.fake_root/media/external-disk/.Trash/')
        having_file('.fake_root/media/external-disk/.Trash/123/info/foo.trashinfo')
        empty=EmptyCmd(
                out          = StringIO(),
                err          = StringIO(),
                environ      = {},
                getuid       = lambda: 123,
                list_volumes = lambda: ['.fake_root/media/external-disk'],
                )
        empty.run('trash-empty')
        assert not os.path.exists('.fake_root/media/external-disk/.Trash/123/info/foo.trashinfo')
    def test_it_removes_trashinfos_from_method_2_dir(self):
        require_empty_dir('.fake_root')
        having_file('.fake_root/media/external-disk/.Trash-123/info/foo.trashinfo')
        empty=EmptyCmd(
                out          = StringIO(),
                err          = StringIO(),
                environ      = {},
                getuid       = lambda: 123,
                list_volumes = lambda: ['.fake_root/media/external-disk'],
                )
        empty.run('trash-empty')
        assert not os.path.exists('.fake_root/media/external-disk/.Trash-123/info/foo.trashinfo')

class TestTrashEmpty_on_help:
    def test_help_output(self):
        err, out = StringIO(), StringIO()
        cmd = EmptyCmd(err = err,
                       out = out,
                       environ = {},)
        cmd.run('trash-empty', '--help')
        assert_equals(out.getvalue(), """\
Usage: trash-empty [days]

Purge trashed files.

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""")

class TestTrashEmpty_on_version():
    def test_it_print_version(self):
        err, out = StringIO(), StringIO()
        cmd = EmptyCmd(err = err,
                       out = out,
                       environ = {},
                       version = '1.2.3')
        cmd.run('trash-empty', '--version')
        assert_equals(out.getvalue(), """\
trash-empty 1.2.3
""")

def date(yyyy_mm_dd):
    from datetime import datetime
    return datetime.strptime(yyyy_mm_dd, '%Y-%m-%d')

