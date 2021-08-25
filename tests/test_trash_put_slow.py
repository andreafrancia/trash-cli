# Copyright (C) 2009-2020 Andrea Francia Trivolzio(PV) Italy
import pytest

import os
from os.path import exists as file_exists

from . import run_command
from .files import make_empty_file, require_empty_dir
from .support import MyPath
from .files import make_sticky_dir
from trashcli.fs import read_file
from .asserts import assert_line_in_text
import unittest


class TrashPutFixture:

    def __init__(self):
        self.temp_dir = MyPath.make_temp_dir()

    def run_trashput(self, *args):
        self.environ = {'XDG_DATA_HOME': self.temp_dir / 'XDG_DATA_HOME',
                        'HOME': self.temp_dir / 'home'}
        result = run_command.run_command(self.temp_dir,
                                         "trash-put",
                                         list(args),
                                         env=self.environ)
        self.stdout = result.stdout
        self.stderr = result.stderr
        self.exit_code = result.exit_code


@pytest.mark.slow
class TestDeletingExistingFile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        env = {'XDG_DATA_HOME': self.temp_dir / 'XDG_DATA_HOME' }
        make_empty_file(self.temp_dir / 'foo')
        self.result = run_command.run_command(self.temp_dir, "trash-put",
                                              [self.temp_dir / 'foo'],
                                              env=env)

    def test_it_should_remove_the_file(self):
        assert not file_exists(self.temp_dir / 'foo')

    def test_it_should_remove_it_silently(self):
        self.assertEqual("", self.result.stdout)

    def test_a_trashinfo_file_should_have_been_created(self):
        read_file(self.temp_dir / 'XDG_DATA_HOME/Trash/info/foo.trashinfo')

    def tearDown(self):
        self.temp_dir.clean_up()

@pytest.mark.slow
class Test_when_deleting_an_existing_file_in_verbose_mode(unittest.TestCase):
    def setUp(self):
        self.fixture = TrashPutFixture()
        self.foo_file = self.fixture.temp_dir / "foo"
        make_empty_file(self.foo_file)
        self.fixture.run_trashput('-v', self.foo_file)

    def test_should_tell_where_a_file_is_trashed(self):
        output = self.fixture.stderr.splitlines()
        expected_line = "trash-put: '%s' trashed in %s/XDG_DATA_HOME/Trash" % \
                        (self.foo_file, self.fixture.temp_dir)
        assert (expected_line in output)

    def test_should_be_succesfull(self):
        assert 0 == self.fixture.exit_code


@pytest.mark.slow
class Test_when_deleting_a_non_existing_file(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fixture = TrashPutFixture()

    def test_should_be_succesfull(self):
        self.fixture.run_trashput('-v', self.tmp_dir / 'non-existent')
        assert 0 != self.fixture.exit_code

    def tearDown(self):
        self.tmp_dir.clean_up()


@pytest.mark.slow
class Test_when_fed_with_dot_arguments(unittest.TestCase):

    def setUp(self):
        self.fixture = TrashPutFixture()

    def test_dot_argument_is_skipped(self):

        self.fixture.run_trashput(".")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        self.assertEqual("trash-put: cannot trash directory '.'\n",
                         self.fixture.stderr)

    def test_dot_dot_argument_is_skipped(self):

        self.fixture.run_trashput("..")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        self.assertEqual("trash-put: cannot trash directory '..'\n",
                         self.fixture.stderr)

    def test_dot_argument_is_skipped_even_in_subdirs(self):
        sandbox = MyPath.make_temp_dir()

        self.fixture.run_trashput("%s/." % sandbox)

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        self.assertEqual("trash-put: cannot trash '.' directory '%s/.'\n" %
                         sandbox,
                         self.fixture.stderr)

        assert file_exists(sandbox)
        sandbox.clean_up()

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self):
        sandbox = MyPath.make_temp_dir()

        self.fixture.run_trashput("%s/.." % sandbox)

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be written on stderr
        self.assertEqual("trash-put: cannot trash '..' directory '%s/..'\n" %
                         sandbox,
                         self.fixture.stderr)

        assert file_exists(sandbox)
        sandbox.clean_up()


@pytest.mark.slow
class TestUnsecureTrashDirMessages(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        self.fake_vol = self.temp_dir / 'fake-vol'
        self.fixture = TrashPutFixture()
        require_empty_dir(self.fake_vol)
        make_empty_file(self.fake_vol / 'foo')

    def test_when_is_unsticky(self):
        require_empty_dir(self.fake_vol / '.Trash')

        self.fixture.run_trashput('--force-volume', self.fake_vol,
                                  '-v',
                                  self.fake_vol / 'foo')

        assert_line_in_text(
                'trash-put: found unsecure .Trash dir (should be sticky): ' +
                self.fake_vol / '.Trash', self.fixture.stderr)

    def test_when_it_is_not_a_dir(self):
        make_empty_file(self.fake_vol / '.Trash')

        self.fixture.run_trashput('--force-volume', self.fake_vol,
                                  '-v',
                                  self.fake_vol / 'foo')

        assert_line_in_text(
                'trash-put: found unusable .Trash dir (should be a dir): ' +
                self.fake_vol / '.Trash', self.fixture.stderr)

    def test_when_is_a_symlink(self):
        make_sticky_dir( self.fake_vol / 'link-destination')
        os.symlink('link-destination',  self.fake_vol / '.Trash')

        self.fixture.run_trashput('--force-volume', self.fake_vol,
                                  '-v', self.fake_vol / 'foo')

        assert_line_in_text(
                'trash-put: found unsecure .Trash dir (should not be a symlink): ' +
                self.fake_vol / '.Trash', self.fixture.stderr)

    def tearDown(self):
        self.temp_dir.clean_up()
