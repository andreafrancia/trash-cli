from unittest import TestCase
from nose.tools import assert_equals
import os
from trashcli.trash import TrashDirectory

class TestTrashDirectory(TestCase) :

    def test_str_uses_tilde(self):
        os.environ['HOME']='/home/user'
        self.trash_dir = "/home/user/.local/share/Trash"
        self.assert_name_is('~/.local/share/Trash')

    def test_str_dont_uses_tilde(self):
        os.environ['HOME']='/home/user'
        self.trash_dir = "/not-in-home/Trash"
        self.assert_name_is('/not-in-home/Trash')

    def test_str_uses_tilde_with_trailing_slashes(self):
        os.environ['HOME']='/home/user/'
        self.trash_dir = "/home/user/.local/share/Trash"
        self.assert_name_is('~/.local/share/Trash')

    def test_str_uses_tilde_with_trailing_slash(self):
        os.environ['HOME']='/home/user////'
        self.trash_dir = "/home/user/.local/share/Trash"
        self.assert_name_is('~/.local/share/Trash')

    def test_str_with_empty_home(self):
        os.environ['HOME']=''
        self.trash_dir = "/foo/Trash"
        self.assert_name_is('/foo/Trash')

    def assert_name_is(self, expected_name):
        trash_dir = TrashDirectory(self.trash_dir, '/')
        assert_equals(expected_name, trash_dir.name())


