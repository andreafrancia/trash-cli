import unittest

from mock import Mock

from integration_tests.files import require_empty_dir
from trashcli.put import TopTrashDirRules


class TestTopTrashDirRules(unittest.TestCase):
    def setUp(self):
        require_empty_dir('sandbox')
        self.fs = Mock()
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = True
        self.rules = TopTrashDirRules()
        self.out = Mock()

    def test_check_when_no_sticky_bit(self):
        self.fs.has_sticky_bit.return_value = False

        self.check_rules()

        self.out.not_valid_parent_should_be_sticky.assert_called_with()

    def test_check_when_no_dir(self):
        self.fs.isdir.return_value = False

        self.check_rules()

        self.out.not_valid_should_be_a_dir.assert_called_with()

    def test_check_when_is_symlink(self):
        self.fs.islink.return_value = True

        self.check_rules()

        self.out.not_valid_parent_should_not_be_a_symlink.assert_called_with()

    def test_check_pass(self):

        self.check_rules()

        self.out.is_valid()

    def check_rules(self):
        self.rules.check_trash_dir_is_secure('sandbox/trash-dir/123',
                                             self.out,
                                             self.fs)
