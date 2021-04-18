import unittest

from mock import Mock

from trashcli.put import TopTrashDirRules


class TestTopTrashDirRules(unittest.TestCase):
    def setUp(self):
        self.fs = Mock()
        self.rules = TopTrashDirRules()
        self.out = Mock()

    def test_check_when_no_sticky_bit(self):
        self.assume_the_directory_is_ok()
        self.but_it_does_not_have_the_sticky_bit()

        self.check_rules()

        self.out.not_valid_parent_should_be_sticky.assert_called_with()
        self.fs.has_sticky_bit.assert_called_with('/volume/.Trash')

    def test_check_when_no_dir(self):
        self.assume_the_directory_is_ok()
        self.but_it_is_not_a_dir()

        self.check_rules()

        self.out.not_valid_should_be_a_dir.assert_called_with()
        self.fs.isdir.assert_called_with('/volume/.Trash')

    def test_check_when_is_symlink(self):
        self.assume_the_directory_is_ok()
        self.but_it_is_a_link()

        self.check_rules()

        self.out.not_valid_parent_should_not_be_a_symlink.assert_called_with()
        self.fs.islink.assert_called_with('/volume/.Trash')

    def test_check_pass(self):
        self.assume_the_directory_is_ok()

        self.check_rules()

        self.out.is_valid()

    def check_rules(self):
        self.rules.check_trash_dir_is_secure('/volume/.Trash/123',
                                             self.out,
                                             self.fs)

    def assume_the_directory_is_ok(self):
        self.fs.isdir.return_value = True
        self.fs.islink.return_value = False
        self.fs.has_sticky_bit.return_value = True

    def but_it_does_not_have_the_sticky_bit(self):
        self.fs.has_sticky_bit.return_value = False

    def but_it_is_not_a_dir(self):
        self.fs.isdir.return_value = False

    def but_it_is_a_link(self):
        self.fs.islink.return_value = True

