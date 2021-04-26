import unittest

from mock import Mock, call

from trashcli.put import TopTrashDirRules


class TestTopTrashDirRules(unittest.TestCase):
    def setUp(self):
        self.fs = Mock()
        self.rules = TopTrashDirRules()

    def test_not_valid_should_be_a_dir(self):
        fs = Mock(spec=['isdir'])
        fs.isdir.return_value = False

        result = self.rules.check_trash_dir_is_secure('/parent/trash-dir',
                                                      fs)

        assert [call.isdir('/parent')] == fs.mock_calls
        assert ('not_valid_should_be_a_dir', '/parent') == result

    def test_not_valid_parent_should_not_be_a_symlink(self):
        fs = Mock(spec=['isdir', 'islink'])
        fs.isdir.return_value = True
        fs.islink.return_value = True

        result = self.rules.check_trash_dir_is_secure('/parent/trash-dir',
                                                      fs)

        assert [call.isdir('/parent'),
                call.islink('/parent')] == fs.mock_calls
        assert ('not_valid_parent_should_not_be_a_symlink', '/parent') == result

    def test_not_valid_parent_should_be_sticky(self):
        fs = Mock(spec=['isdir', 'islink', 'has_sticky_bit'])
        fs.isdir.return_value = True
        fs.islink.return_value = False
        fs.has_sticky_bit.return_value = False

        result = self.rules.check_trash_dir_is_secure('/parent/trash-dir',
                                                      fs)

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == fs.mock_calls
        assert ('not_valid_parent_should_be_sticky', '/parent') == result

    def test_is_valid(self):
        fs = Mock(spec=['isdir', 'islink', 'has_sticky_bit'])
        fs.isdir.return_value = True
        fs.islink.return_value = False
        fs.has_sticky_bit.return_value = True

        result = self.rules.check_trash_dir_is_secure('/parent/trash-dir',
                                                      fs)

        assert [call.isdir('/parent'),
                call.islink('/parent'),
                call.has_sticky_bit('/parent')] == fs.mock_calls
        assert ('is_valid', None) == result
