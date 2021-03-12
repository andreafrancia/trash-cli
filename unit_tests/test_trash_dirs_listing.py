# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest

from trashcli.trash import TrashDirs, TopTrashDirValidationResult
from mock import Mock
from mock import MagicMock
from trashcli.trash import TopTrashDirRules


class TestTrashDirs_listing(unittest.TestCase):

    def test_the_method_2_is_always_in(self):
        self.uid = 123
        self.volumes = ['/usb']

        assert '/usb/.Trash-123' in self.trashdirs()

    def test_the_method_1_is_in_if_it_is_a_sticky_dir(self):
        self.uid = 123
        self.volumes = ['/usb']
        self.having_sticky_Trash_dir()

        assert '/usb/.Trash/123' in self.trashdirs()

    def test_the_method_1_is_not_considered_if_not_sticky_dir(self):
        self.uid = 123
        self.volumes = ['/usb']
        self.having_non_sticky_Trash_dir()

        assert '/usb/.Trash/123' not in self.trashdirs()

    def test_should_return_home_trashcan_when_XDG_DATA_HOME_is_defined(self):
        self.environ['XDG_DATA_HOME'] = '~/.local/share'

        assert '~/.local/share/Trash' in self.trashdirs()

    def trashdirs(self):
        result = []
        def append(trash_dir, volume):
            result.append(trash_dir)
        class FileReader:
            def is_sticky_dir(_, path):
                return self.Trash_dir_is_sticky
            def exists(_, path):
                return True
            def is_symlink(_, path):
                return False
        class FakeTopTrashDirRules:
            def valid_to_be_read(_, path):
                if self.Trash_dir_is_sticky:
                    return TopTrashDirValidationResult.Valid
                else:
                    return TopTrashDirValidationResult.NotValidBecauseIsNotSticky
        trash_dirs = TrashDirs(
            environ=self.environ,
            getuid=lambda:self.uid,
            top_trashdir_rules = FakeTopTrashDirRules(),
            list_volumes = lambda: self.volumes,
        )
        trash_dirs.on_trash_dir_found = append
        trash_dirs.list_trashdirs()
        return result

    def setUp(self):
        self.uid = -1
        self.volumes = ()
        self.Trash_dir_is_sticky = not_important_for_now()
        self.environ = {}
    def having_sticky_Trash_dir(self): self.Trash_dir_is_sticky = True
    def having_non_sticky_Trash_dir(self): self.Trash_dir_is_sticky = False

def not_important_for_now(): None


class TestDescribe_AvailableTrashDirs_when_parent_is_unsticky(unittest.TestCase):
    def setUp(self):
        self.fs = MagicMock()
        self.dirs = TrashDirs(environ = {},
                              getuid = lambda:123,
                              top_trashdir_rules = TopTrashDirRules(self.fs),
                              list_volumes = lambda: ['/topdir'],
                              )
        self.dirs.on_trashdir_skipped_because_parent_not_sticky = Mock()
        self.dirs.on_trashdir_skipped_because_parent_is_symlink = Mock()
        self.fs.is_sticky_dir.side_effect = (
                lambda path: {'/topdir/.Trash':False}[path])

    def test_it_should_report_skipped_dir_non_sticky(self):
        self.fs.exists.side_effect = (
                lambda path: {'/topdir/.Trash/123':True}[path])

        self.dirs.list_trashdirs()

        (self.dirs.on_trashdir_skipped_because_parent_not_sticky.
                assert_called_with('/topdir/.Trash/123'))

    def test_it_shouldnot_care_about_non_existent(self):
        self.fs.exists.side_effect = (
                lambda path: {'/topdir/.Trash/123':False}[path])

        self.dirs.list_trashdirs()

        assert [] == self.dirs.on_trashdir_skipped_because_parent_not_sticky.mock_calls


class TestDescribe_AvailableTrashDirs_when_parent_is_symlink(unittest.TestCase):
    def setUp(self):
        self.fs = MagicMock()
        self.dirs = TrashDirs(environ = {},
                              getuid = lambda:123,
                              top_trashdir_rules = TopTrashDirRules(self.fs),
                              list_volumes = lambda: ['/topdir'])
        self.fs.exists.side_effect = (lambda path: {'/topdir/.Trash/123':True}[path])
        self.symlink_error = Mock()
        self.dirs.on_trashdir_skipped_because_parent_is_symlink = self.symlink_error


    def test_it_should_skip_symlink(self):
        self.fs.is_sticky_dir.return_value = True
        self.fs.is_symlink.return_value    = True

        self.dirs.list_trashdirs()

        self.symlink_error.assert_called_with('/topdir/.Trash/123')

