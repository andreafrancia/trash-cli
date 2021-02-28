# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from trashcli.put import TrashPutCmd

import os
from os.path import exists as file_exists
from datetime import datetime

from unit_tests import myStringIO
from .files import make_empty_file, require_empty_dir, MyPath, read_file
from .files import make_sticky_dir
from trashcli.fstab import FakeFstab
from trashcli.fs import remove_file
from trashcli.put import parent_path, RealFs
from .asserts import assert_line_in_text
import unittest


class TestPath(unittest.TestCase):
    def setUp(self):
        self.base = os.path.realpath(os.getcwd())

    def test(self):
        require_empty_dir('other_dir/dir')
        remove_file('dir')
        os.symlink('other_dir/dir', 'dir')
        make_empty_file('dir/foo')
        assert (os.path.join(self.base, 'other_dir/dir') ==
                     parent_path('dir/foo'))
        remove_file('dir')
        remove_file('other_dir')
    def test2(self):
        require_empty_dir('test-disk/dir')
        remove_file('link-to-non-existent')
        os.symlink('test-disk/non-existent', 'link-to-non-existent')
        assert (self.base ==
                     parent_path('link-to-non-existent'))
        remove_file('link-to-non-existent')

    def test3(self):
        remove_file('foo')
        remove_file('bar')
        require_empty_dir('foo')
        require_empty_dir('bar')
        os.symlink('../bar/zap', 'foo/zap')
        assert os.path.join(self.base, 'foo') == parent_path('foo/zap')
        remove_file('foo')
        remove_file('bar')

    def test4(self):
        remove_file('foo')
        remove_file('bar')
        require_empty_dir('foo')
        require_empty_dir('bar')
        os.symlink('../bar/zap', 'foo/zap')
        make_empty_file('bar/zap')
        assert os.path.join(self.base,'foo') == parent_path('foo/zap')
        remove_file('foo')
        remove_file('bar')

class TrashPutFixture:

    def __init__(self):
        self.fstab   = FakeFstab()
        self.temp_dir = MyPath.make_temp_dir()

    def run_trashput(self, *argv):
        self.environ = {'XDG_DATA_HOME': self.temp_dir / 'XDG_DATA_HOME' }
        self.out = myStringIO.StringIO()
        self.err = myStringIO.StringIO()
        cmd = TrashPutCmd(
            stdout      = self.out,
            stderr      = self.err,
            environ     = self.environ,
            volume_of   = self.fstab.volume_of,
            parent_path = os.path.dirname,
            realpath    = lambda x:x,
            fs          = RealFs(),
            getuid      = lambda: None,
            now         = datetime.now
        )
        self.exit_code = cmd.run(list(argv))
        self.stdout = self.out.getvalue()
        self.stderr = self.err.getvalue()


class Test_when_deleting_an_existing_file(unittest.TestCase):
    def setUp(self):
        self.fixture = TrashPutFixture()
        make_empty_file(self.fixture.temp_dir / 'foo')
        self.fixture.run_trashput('trash-put', self.fixture.temp_dir / 'foo')

    def test_it_should_remove_the_file(self):
        assert not file_exists(self.fixture.temp_dir / 'foo')

    def test_it_should_remove_it_silently(self):
        self.assertEqual("", self.fixture.stdout)

    def test_a_trashinfo_file_should_have_been_created(self):
        read_file(self.fixture.temp_dir / 'XDG_DATA_HOME/Trash/info/foo.trashinfo')

class Test_when_deleting_an_existing_file_in_verbose_mode(unittest.TestCase):
    def setUp(self):
        self.fixture = TrashPutFixture()
        self.foo_file = self.fixture.temp_dir / "foo"
        make_empty_file(self.foo_file)
        self.fixture.run_trashput('trash-put', '-v', self.foo_file)

    def test_should_tell_where_a_file_is_trashed(self):
        output = self.fixture.stderr.splitlines()
        assert (("trash-put: '%s' trashed in %s/XDG_DATA_HOME/Trash" %
                 (self.foo_file, self.fixture.temp_dir)) in
                  output)

    def test_should_be_succesfull(self):
        assert 0 == self.fixture.exit_code


class Test_when_deleting_a_non_existing_file(unittest.TestCase):
    def setUp(self):
        self.fixture = TrashPutFixture()
        self.fixture.run_trashput('trash-put', '-v', 'non-existent')

    def test_should_be_succesfull(self):
        assert 0 != self.fixture.exit_code


class Test_when_fed_with_dot_arguments(unittest.TestCase):

    def setUp(self):
        self.fixture = TrashPutFixture()

    def test_dot_argument_is_skipped(self):

        self.fixture.run_trashput("trash-put", ".")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        self.assertEqual("trash-put: cannot trash directory '.'\n",
                         self.fixture.stderr)

    def test_dot_dot_argument_is_skipped(self):

        self.fixture.run_trashput("trash-put", "..")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.assertEqual("trash-put: cannot trash directory '..'\n",
                         self.fixture.stderr)

    def test_dot_argument_is_skipped_even_in_subdirs(self):
        sandbox = MyPath.make_temp_dir()

        self.fixture.run_trashput("trash-put", "%s/." % sandbox)

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.assertEqual("trash-put: cannot trash '.' directory '%s/.'\n" %
                         sandbox,
                         self.fixture.stderr)

        assert file_exists(sandbox)
        sandbox.clean_up()

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self):
        sandbox = MyPath.make_temp_dir()

        self.fixture.run_trashput("trash-put", "%s/.." % sandbox)

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.assertEqual("trash-put: cannot trash '..' directory '%s/..'\n" %
                         sandbox,
                         self.fixture.stderr)

        assert file_exists(sandbox)
        sandbox.clean_up()


class TestUnsecureTrashDirMessages(unittest.TestCase):
    def setUp(self):
        self.fixture = TrashPutFixture()
        self.temp_dir = MyPath.make_temp_dir()
        self.fake_vol = self.temp_dir / 'fake-vol'
        require_empty_dir(self.fake_vol)
        self.fixture.fstab.add_mount(self.fake_vol)
        make_empty_file(self.fake_vol / 'foo')

    def test_when_is_unsticky(self):
        require_empty_dir(self.fake_vol / '.Trash')

        self.fixture.run_trashput('trash-put', '-v', self.fake_vol / 'foo')

        assert_line_in_text(
                'trash-put: found unsecure .Trash dir (should be sticky): ' +
                self.fake_vol / '.Trash', self.fixture.stderr)

    def test_when_it_is_not_a_dir(self):
        make_empty_file(self.fake_vol / '.Trash')

        self.fixture.run_trashput('trash-put', '-v', self.fake_vol / 'foo')

        assert_line_in_text(
                'trash-put: found unusable .Trash dir (should be a dir): ' +
                self.fake_vol / '.Trash', self.fixture.stderr)

    def test_when_is_a_symlink(self):
        make_sticky_dir( self.fake_vol / 'link-destination')
        os.symlink('link-destination',  self.fake_vol / '.Trash')

        self.fixture.run_trashput('trash-put', '-v', self.fake_vol / 'foo')

        assert_line_in_text(
                'trash-put: found unsecure .Trash dir (should not be a symlink): ' +
                self.fake_vol / '.Trash', self.fixture.stderr)

    def tearDown(self):
        self.temp_dir.clean_up()
