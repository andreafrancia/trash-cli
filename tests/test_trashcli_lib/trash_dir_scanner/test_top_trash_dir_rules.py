import unittest

from tests.support.py2mock import Mock, call
from trashcli.trash_dirs_scanner import (
    TopTrashDirRules,
    top_trash_dir_does_not_exist,
    top_trash_dir_invalid_because_not_sticky,
    top_trash_dir_invalid_because_parent_is_symlink,
    top_trash_dir_valid,
)


class TestTopTrashDirRules(unittest.TestCase):
    def setUp(self):
        self.fs = Mock(spec=['path_exists', 'is_sticky_dir', 'is_symlink'])
        self.rules = TopTrashDirRules(self.fs)

    def test_path_not_exists(self):
        self.fs.path_exists.return_value = False

        result = self.rules.valid_to_be_read("/path")

        assert (result, self.fs.mock_calls) == \
               (top_trash_dir_does_not_exist,
                [call.path_exists('/path')])

    def test_parent_not_sticky(self):
        self.fs.path_exists.return_value = True
        self.fs.is_sticky_dir.return_value = False

        result = self.rules.valid_to_be_read("/path")

        assert (result, self.fs.mock_calls) == \
               (top_trash_dir_invalid_because_not_sticky,
                [call.path_exists('/path'),
                 call.is_sticky_dir('/')])

    def test_parent_is_symlink(self):
        self.fs.path_exists.return_value = True
        self.fs.is_sticky_dir.return_value = True
        self.fs.is_symlink.return_value = True

        result = self.rules.valid_to_be_read("/path")

        assert (result, self.fs.mock_calls) == \
               (top_trash_dir_invalid_because_parent_is_symlink,
                [call.path_exists('/path'),
                 call.is_sticky_dir('/'),
                 call.is_symlink('/')])

    def test_parent_is_sym(self):
        self.fs.path_exists.return_value = True
        self.fs.is_sticky_dir.return_value = True
        self.fs.is_symlink.return_value = False

        result = self.rules.valid_to_be_read("/path")

        assert (result, self.fs.mock_calls) == \
               (top_trash_dir_valid,
                [call.path_exists('/path'),
                 call.is_sticky_dir('/'),
                 call.is_symlink('/')])
