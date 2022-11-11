import unittest

from mock import Mock, call
from trashcli.put.candidate import Candidate

from trashcli.put.security_check import SecurityCheck, top_trash_dir_rules


class TestTopTrashDirRules(unittest.TestCase):
    def setUp(self):
        self.fs = Mock(spec=['isdir', 'islink', 'has_sticky_bit'])
        self.check = SecurityCheck(self.fs)

    def test_not_valid_should_be_a_dir(self):
        self.fs.isdir.return_value = False

        secure, messages = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', top_trash_dir_rules))

        assert [call.isdir('/parent')] == self.fs.mock_calls
        assert secure == False
        assert messages == [
            'found unusable .Trash dir (should be a dir): /parent']

    def test_not_valid_parent_should_not_be_a_symlink(self):
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = True

        secure, messages = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', top_trash_dir_rules))

        assert [call.isdir('/parent'),
                call.islink('/parent')] == self.fs.mock_calls
        assert secure == False
        assert messages == [
            'found unsecure .Trash dir (should not be a symlink): /parent']

    def test_not_valid_parent_should_be_sticky(self):
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = False

        secure, messages = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', top_trash_dir_rules))

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == self.fs.mock_calls
        assert False == secure
        assert messages == [
            'found unsecure .Trash dir (should be sticky): /parent']

    def test_is_valid(self):
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = True

        secure, messages = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', top_trash_dir_rules))

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == self.fs.mock_calls
        assert secure == True
        assert messages == []


def make_candidate(trash_dir_path, check_type):
    return Candidate(trash_dir_path=trash_dir_path,
                     volume=None,
                     path_maker_type=None,
                     check_type=check_type,
                     gate=None)
