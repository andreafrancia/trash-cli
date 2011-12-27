# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import istest
from .files import having_file, require_empty_dir, having_empty_dir
from trashcli.trash import TrashPutCmd

@istest
class describe_trash_put_command_when_deleting_a_file:

    @istest
    def it_should_remove_the_file(self):

        file_should_have_been_deleted('sandbox/foo')

    @istest
    def it_should_remove_it_silently(self):

        self.output_should_be('')

    def a_trashinfo_file_should_have_been_created(self):
        
        file('sandbox/XDG_DATA_HOME/Trash/info/foo.trashinfo').read()

    def setUp(self):
        require_empty_dir('sandbox')

        having_file('sandbox/foo')
        self.run_trashput = TrashPutRunner(
                environ = {'XDG_DATA_HOME': 'sandbox/XDG_DATA_HOME' }
        )
        
        self.stderr_should_be = self.run_trashput.err.should_be
        self.output_should_be = self.run_trashput.out.should_be

        self.run_trashput('trash-put', 'sandbox/foo')

import os
exists = os.path.exists
@istest
class describe_trash_put_command_on_dot_arguments:

    def test_dot_argument_is_skipped(self):
        having_file('other_argument')

        self.run_trashput("trash-put", ".", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
                "trash-put: cannot trash directory `.'\n")

        # the remaining arguments should be processed
        assert not exists('other_argument')

    def test_dot_dot_argument_is_skipped(self):
        having_file('other_argument')

        self.run_trashput("trash-put", "..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash directory `..'\n")

        # the remaining arguments should be processed
        assert not exists('other_argument')

    def test_dot_argument_is_skipped_even_in_subdirs(self):
        having_empty_dir('sandbox/')
        having_file('other_argument')

        self.run_trashput("trash-put", "sandbox/.", "other_argument")

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

        self.run_trashput("trash-put", "sandbox/..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        self.stderr_should_be(
            "trash-put: cannot trash `..' directory `sandbox/..'\n")

        # the remaining arguments should be processed
        assert not exists('other_argument')
        assert exists('sandbox')

    def setUp(self):
        self.run_trashput = TrashPutRunner()
        self.stderr_should_be = self.run_trashput.err.should_be
        
class TrashPutRunner:
    def __init__(self, environ = os.environ):
        from .output_collector import OutputCollector
        self.out     = OutputCollector()
        self.err     = OutputCollector()
        self.environ = environ
    def __call__(self, *argv):
        TrashPutCmd( 
            stdout  = self.out,
            stderr  = self.err,
            environ = self.environ
        ).run(list(argv))

def file_should_have_been_deleted(path):
    import os
    assert not os.path.exists('sandbox/foo')

