# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
from trashcli.put import TrashPutCmd

import os
from os.path import exists as file_exists
from datetime import datetime

from .files import make_empty_file, require_empty_dir
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

class TrashPutTest(unittest.TestCase):

    def setUp(self):
        self.prepare_fixture()
        self.setUp2()

    def setUp2(self):
        pass

    def prepare_fixture(self):
        require_empty_dir('sandbox')
        self.environ = {'XDG_DATA_HOME': 'sandbox/XDG_DATA_HOME' }

        from .output_collector import OutputCollector
        self.out     = OutputCollector()
        self.err     = OutputCollector()
        self.fstab   = FakeFstab()

        self.stderr_should_be = self.err.should_be
        self.output_should_be = self.out.should_be

    def run_trashput(self, *argv):
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
        self.stderr = self.err.getvalue()


class Test_when_deleting_an_existing_file(TrashPutTest):
    def setUp2(self):
        make_empty_file('sandbox/foo')
        self.run_trashput('trash-put', 'sandbox/foo')

    def test_it_should_remove_the_file(self):
        assert not file_exists('sandbox/foo')

    def test_it_should_remove_it_silently(self):
        self.output_should_be('')

    def test_a_trashinfo_file_should_have_been_created(self):
        open('sandbox/XDG_DATA_HOME/Trash/info/foo.trashinfo').read()

class Test_when_deleting_an_existing_file_in_verbose_mode(TrashPutTest):
    def setUp2(self):
        make_empty_file('sandbox/foo')
        self.run_trashput('trash-put', '-v', 'sandbox/foo')

    def test_should_tell_where_a_file_is_trashed(self):
        assert ("trash-put: 'sandbox/foo' trashed in sandbox/XDG_DATA_HOME/Trash" in
                  self.stderr.splitlines())

    def test_should_be_succesfull(self):
        assert 0 == self.exit_code


class Test_when_deleting_a_non_existing_file(TrashPutTest):
    def setUp2(self):
        self.run_trashput('trash-put', '-v', 'non-existent')

    def test_should_be_succesfull(self):
        assert 0 != self.exit_code


class Test_when_fed_with_dot_arguments(TrashPutTest):

    def setUp2(self):
        require_empty_dir('sandbox/')
        make_empty_file('other_argument')

    def test_dot_argument_is_skipped(self):

        self.run_trashput("trash-put", ".", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
                "trash-put: cannot trash directory '.'\n")

        # the remaining arguments should be processed
        assert not file_exists('other_argument')

    def test_dot_dot_argument_is_skipped(self):

        self.run_trashput("trash-put", "..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash directory '..'\n")

        # the remaining arguments should be processed
        assert not file_exists('other_argument')

    def test_dot_argument_is_skipped_even_in_subdirs(self):

        self.run_trashput("trash-put", "sandbox/.", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash '.' directory 'sandbox/.'\n")

        # the remaining arguments should be processed
        assert not file_exists('other_argument')
        assert file_exists('sandbox')

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self):

        self.run_trashput("trash-put", "sandbox/..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash '..' directory 'sandbox/..'\n")

        # the remaining arguments should be processed
        assert not file_exists('other_argument')
        assert file_exists('sandbox')


class TestUnsecureTrashDirMessages(TrashPutTest):
    def setUp(self):
        TrashPutTest.setUp(self)
        require_empty_dir('fake-vol')
        self.fstab.add_mount('fake-vol')
        make_empty_file('fake-vol/foo')

    def test_when_is_unsticky(self):
        require_empty_dir('fake-vol/.Trash')

        self.run_trashput('trash-put', '-v', 'fake-vol/foo')

        assert_line_in_text(
                'trash-put: found unsecure .Trash dir (should be sticky): '
                'fake-vol/.Trash', self.stderr)

    def test_when_it_is_not_a_dir(self):
        make_empty_file('fake-vol/.Trash')

        self.run_trashput('trash-put', '-v', 'fake-vol/foo')

        assert_line_in_text(
                'trash-put: found unusable .Trash dir (should be a dir): '
                'fake-vol/.Trash', self.stderr)

    def test_when_is_a_symlink(self):
        make_sticky_dir('fake-vol/link-destination')
        os.symlink('link-destination', 'fake-vol/.Trash')

        self.run_trashput('trash-put', '-v', 'fake-vol/foo')

        assert_line_in_text(
                'trash-put: found unsecure .Trash dir (should not be a symlink): '
                'fake-vol/.Trash', self.stderr)

