# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import istest
from .files import having_file, require_empty_dir, touch, having_empty_dir
from trashcli.trash import TrashPutCmd
from StringIO import StringIO

@istest
class describe_trash_put_command_when_deleting_a_file:

    @istest
    def it_should_remove_the_file(self):

        file_should_have_been_deleted('sandbox/foo')

    @istest
    def it_should_remove_it_silently(self):

        self.output_should_be_equal_to('')

    def setUp(self):
        require_empty_dir('sandbox')

        having_file('sandbox/foo')
        self.run_trashput('sandbox/foo')

    def run_trashput(self, *args):
        self.out = StringIO()
        self.err = StringIO()
        cmd = TrashPutCmd(stdout = self.out, stderr = self.err)
        cmd.run(['trash-put'] + list(args))

    def output_should_be_equal_to(self, expected):
        actual = self.out.getvalue()
        assert actual == expected

import os
exists = os.path.exists
@istest
class describe_trash_put_command2:

    def test_dot_argument_is_skipped(self):
        having_file('other_argument')

        self.run_trash_put("trash-put", ".", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
                "trash-put: cannot trash directory `.'\n")

        # the remaining arguments should be processed
        assert not exists('other_argument')

    def test_dot_dot_argument_is_skipped(self):
        having_file('other_argument')

        self.run_trash_put("trash-put", "..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash directory `..'\n")

        # the remaining arguments should be processed
        assert not exists('other_argument')

    def test_dot_argument_is_skipped_even_in_subdirs(self):
        having_empty_dir('sandbox/')
        having_file('other_argument')

        self.run_trash_put("trash-put", "sandbox/.", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash `.' directory `sandbox/.'\n")

        # the remaining arguments should be processed
        assert not exists('other_argument')
        assert exists('sandbox')

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self):
        having_empty_dir('sandbox')
        having_file('other_argument')

        self.run_trash_put("trash-put", "sandbox/..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash `..' directory `sandbox/..'\n")

        # the remaining arguments should be processed
        assert not exists('other_argument')
        assert exists('sandbox')

    def run_trash_put(self, *argv):
        from .output_collector import OutputCollector
        self.out = OutputCollector()
        self.err = OutputCollector()
        cmd = TrashPutCmd(stdout = self.out, stderr = self.err)
        cmd.run(list(argv))

    def stderr_should_be(self, expected):
        self.err.should_be(expected)

def file_should_have_been_deleted(path):
    import os
    assert not os.path.exists('sandbox/foo')

