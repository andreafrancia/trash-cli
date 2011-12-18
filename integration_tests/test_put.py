# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

from unittest import TestCase
from trashcli.trash import mkdirs
from trashcli.trash import HomeTrashDirectory
from integration_tests.files import require_empty_dir
from nose.tools import assert_equals
from nose.tools import assert_true
from nose.tools import assert_false

class PutTest(TestCase):

    def setUp(self):
        from common import create_cmdenv
        self.cmdenv = create_cmdenv()
        self.sandbox = Sandbox()

    # Rule of Silence: When a program has nothing surprising to say, it should say nothing.
    # See also:
    #  - issue #32
    #  - http://www.catb.org/~esr/writings/taouu/taouu.html#rule-silence
    def test_silence_rule(self):
        self.sandbox.create_file('foo')
        self.cmdenv.run('trash-put', 'foo').assert_result(output="")

    def test_dot_argument_is_skipped(self):
        self.sandbox.create_file('other_argument')
        result = self.cmdenv.run("trash-put", ".","other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        assert_equals(result.stderr,"trash-put: cannot trash directory `.'\n")

        # the remaining arguments should be processed
        assert_false(self.sandbox.exists('other_argument'))

    def test_dot_dot_argument_is_skipped(self):
        self.sandbox.create_file('other_argument')
        result = self.cmdenv.run("trash-put", "..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr

        assert_equals(result.stderr,"trash-put: cannot trash directory `..'\n")

        # the remaining arguments should be processed
        assert_false(self.sandbox.exists('other_argument'))

    def test_dot_argument_is_skipped_even_in_subdirs(self):
        self.sandbox.mkdir('foo')
        self.sandbox.create_file('other_argument')
        result = self.cmdenv.run("trash-put", "foo/.","other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        assert_equals(result.stderr,
            "trash-put: cannot trash `.' directory `foo/.'\n")

        # the remaining arguments should be processed
        assert_false(self.sandbox.exists('other_argument'))
        assert_true(self.sandbox.exists('foo'))

    def test_dot_dot_argument_is_skipped_even_in_subdirs(self):
        self.sandbox.mkdir('foo')
        self.sandbox.create_file('other_argument')
        result = self.cmdenv.run("trash-put", "foo/..", "other_argument")

        # the dot directory shouldn't be operated, but a diagnostic message
        # shall be writtend on stderr
        assert_equals(result.stderr,
            "trash-put: cannot trash `..' directory `foo/..'\n")

        # the remaining arguments should be processed
        assert_false(self.sandbox.exists('other_argument'))
        assert_true(self.sandbox.exists('foo'))

class Sandbox():
    """
    A sandbox where executing commands under tests
    """
    def __init__(self):
        self.path="./sandbox"
        require_empty_dir(self.path)
        mkdirs(self.path)
        self.trashdir = HomeTrashDirectory(
                        './sandbox/home/.local/share/Trash')

    def create_file(self, path, content=None):
        """
        Create a file in sandbox with content
        """
        import os
        file=os.path.join(self.path,path)
        touch(file)
        if content!=None :
            file.write_file(content)

        return file

    def trash(self, path):
        """
        Trash the file in the trash dir at sandbox/home/.local/share/Trash
        """
        result = self.trashdir.trash(path)

        # sanity check
        assert not path.exists()
        return result

    def mkdir(self,subdir):
        import os
        path=os.path.join(self.path, subdir)
        os.mkdir(path)
    def exists(self, path):
        import os
        return os.path.exists(os.path.join(self.path, path))

def touch(path):
    open(path,'a+').close()
