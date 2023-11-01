import unittest
from typing import Tuple, Optional, List

from mock import Mock, call

from trashcli.put.candidate import Candidate
from trashcli.put.core.check_type import TopTrashDirCheck
from trashcli.put.core.either import Either
from trashcli.put.janitor_tools.security_check import SecurityCheck, \
    TrashDirIsNotSecure


class TestTopTrashDirRules(unittest.TestCase):
    def setUp(self):
        self.fs = Mock(spec=['isdir', 'islink', 'has_sticky_bit'])
        self.check = SecurityCheck(self.fs)

    def test_not_valid_should_be_a_dir(self):
        self.fs.isdir.return_value = False

        secure = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', TopTrashDirCheck))

        assert [call.isdir('/parent')] == self.fs.mock_calls
        assert inline(secure) == (False, [
            'found unusable .Trash dir (should be a dir): /parent'])

    def test_not_valid_parent_should_not_be_a_symlink(self):
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = True

        secure = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', TopTrashDirCheck))

        assert [call.isdir('/parent'),
                call.islink('/parent')] == self.fs.mock_calls
        assert inline(secure) == (False, [
            'found unsecure .Trash dir (should not be a symlink): /parent'])

    def test_not_valid_parent_should_be_sticky(self):
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = False

        secure = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', TopTrashDirCheck))

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == self.fs.mock_calls
        assert inline(secure) == (False, [
            'found unsecure .Trash dir (should be sticky): /parent'])

    def test_is_valid(self):
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = True

        secure = self.check.check_trash_dir_is_secure(
            make_candidate('/parent/trash-dir', TopTrashDirCheck))

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == self.fs.mock_calls
        assert inline(secure) == (True, None)


def inline(s,  # type: Either[None, TrashDirIsNotSecure]
           ):  # type: (...) -> Tuple[bool, Optional[List[str]]]
    if s.is_error():
        return False, s.error().messages
    elif s.is_valid():
        return True, s.value()
    else:
        raise ValueError("Should not happen: %s" % s)


def make_candidate(trash_dir_path, check_type):
    return Candidate(trash_dir_path=trash_dir_path,
                     volume=None,
                     path_maker_type=None,
                     check_type=check_type,
                     gate=None)
