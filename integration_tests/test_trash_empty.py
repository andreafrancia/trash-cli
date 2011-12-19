# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals, assert_items_equal
from trashcli.trash2 import EmptyCmd

from StringIO import StringIO
import os
from files import write_file, require_empty_dir, make_dirs, set_sticky_bit
from files import having_file

class TestEmptyCmd():
    def test_it_removes_an_info_file(self):
        self.trash.having_trashinfo('foo.trashinfo')

        self.run()

        self.info_dir.should_be_empty()

    def test_it_removes_multiple_info_files(self):

        self.trash.having_three_trashinfo()

        self.run()

        self.info_dir.should_be_empty()

    def test_it_removes_files(self):
        self.trash.having_one_trashed_file()

        self.run()

        self.files_dir.should_be_empty()
    
    def test_it_keep_unknown_files_in_infodir(self):
        self.info_dir.having_file('not-a-trashinfo')

        self.run()

        self.info_dir.assert_contains_file('not-a-trashinfo')

    def test_it_removes_orphan_files(self):
        self.files_dir.having_orphan_file()

        self.run()

        self.files_dir.should_be_empty()

    def run(self):
        EmptyCmd(
            out = self.out, 
            err = self.err, 
            environ = self.environ).run('trash-empty')

    def setUp(self):
        require_empty_dir('.local')
        self.out=StringIO()
        self.err=StringIO()
        self.environ = { 'XDG_DATA_HOME': '.local' }
        class Dir:
            def __init__(self, path):
                self.path = path
            def having_file(self, child):
                having_file(os.path.join(self.path, child))
            def should_be_empty(self):
                assert self.is_empty()
            def is_empty(self):
                return len(os.listdir(self.path)) == 0
            def having_orphan_file(self):
                # this method makes sense only for files_dir
                self.having_file('a-file-without-any-associated-trashinfo')
                self.assert_contains_file('a-file-without-any-associated-trashinfo')
            def assert_contains_file(self, child):
                assert os.path.exists(os.path.join(self.path, child))
        info_dir  = '.local/Trash/info'
        files_dir = '.local/Trash/files'
        self.info_dir  = Dir(info_dir)
        self.files_dir = Dir(files_dir)
        class TrashDir:
            def having_trashinfo(self, basename_of_trashinfo):
                having_file(os.path.join(info_dir, basename_of_trashinfo))
            def having_three_trashinfo(self):
                self.having_trashinfo('foo.trashinfo')
                self.having_trashinfo('bar.trashinfo')
                self.having_trashinfo('baz.trashinfo')
                assert_items_equal(['foo.trashinfo', 
                                    'bar.trashinfo',
                                    'baz.trashinfo'], os.listdir(info_dir))
            def having_one_trashed_file(self):
                self.having_trashinfo('foo.trashinfo')
                having_file(files_dir +'/foo')
                self.files_dir_should_not_be_empty()
            def files_dir_should_not_be_empty(self):
                assert len(os.listdir(files_dir)) != 0
        self.trash     = TrashDir()

class TestEmptyCmdWithTime:

    def test_it_keeps_files_newer_than_N_days(self):

        self.make_trashinfo('foo', '2000-01-01')
        self.set_now('2000-01-01')

        self.run_trash_emtpy('2')

        assert os.path.exists(self.trashinfo('foo'))

    def test_it_removes_files_older_than_N_days(self):

        self.make_trashinfo('foo', '1999-01-01')
        self.set_now('2000-01-01')

        self.run_trash_emtpy('2')

        assert not os.path.exists(self.trashinfo('foo'))

    def setUp(self):
        self.xdg_data_home='.local'
        require_empty_dir(self.xdg_data_home)

    def make_trashinfo(self, name, date):
        contents = "DeletionDate=%sT00:00:00\n" % date
        write_file(self.trashinfo(name), contents) 

    def trashinfo(self, name):
        return '%(dirname)s/Trash/info/%(name)s.trashinfo' % {
                    'dirname' : self.xdg_data_home,
                    'name'    : name }

    def set_now(self, yyyy_mm_dd):
        self.now = lambda: date(yyyy_mm_dd)

    def run_trash_emtpy(self, *args):
        empty=EmptyCmd( out=StringIO(), 
                        err=StringIO(), 
                        environ={'XDG_DATA_HOME':self.xdg_data_home},
                        now=self.now)
        empty.run('trash-empty', *args)

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

