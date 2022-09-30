import unittest

from mock import Mock, call

from trashcli.put.security_check import top_trash_dir_rules, SecurityCheck


class TestTopTrashDirRules(unittest.TestCase):
    def setUp(self):
        self.fs = Mock()
        self.check = SecurityCheck()

    def test_not_valid_should_be_a_dir(self):
        fs = Mock(spec=['isdir'])
        fs.isdir.return_value = False

        secure, messages = self.check.check_trash_dir_is_secure(
            '/parent/trash-dir', fs, top_trash_dir_rules)

        assert [call.isdir('/parent')] == fs.mock_calls
        assert secure == False
        assert messages == ['found unusable .Trash dir (should be a dir): /parent']

    def test_not_valid_parent_should_not_be_a_symlink(self):
        fs = Mock(spec=['isdir', 'islink'])
        fs.isdir.return_value = True
        fs.islink.return_value = True

        secure, messages = self.check.check_trash_dir_is_secure(
            '/parent/trash-dir', fs, top_trash_dir_rules)

        assert [call.isdir('/parent'),
                call.islink('/parent')] == fs.mock_calls
        assert secure == False
        assert messages == ['found unsecure .Trash dir (should not be a symlink): /parent']

    def test_not_valid_parent_should_be_sticky(self):
        fs = Mock(spec=['isdir', 'islink', 'has_sticky_bit'])
        fs.isdir.return_value = True
        fs.islink.return_value = False
        fs.has_sticky_bit.return_value = False

        secure, messages = self.check.check_trash_dir_is_secure(
            '/parent/trash-dir', fs, top_trash_dir_rules)

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == fs.mock_calls
        assert False == secure
        assert messages == ['found unsecure .Trash dir (should be sticky): /parent']

    def test_is_valid(self):
        fs = Mock(spec=['isdir', 'islink', 'has_sticky_bit'])
        fs.isdir.return_value = True
        fs.islink.return_value = False
        fs.has_sticky_bit.return_value = True

        secure, messages = self.check.check_trash_dir_is_secure(
            '/parent/trash-dir', fs, top_trash_dir_rules)

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == fs.mock_calls
        assert secure == True
        assert messages == []
