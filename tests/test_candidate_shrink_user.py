import unittest

from trashcli.put.core.candidate import Candidate


class TestCandidateShrinkUser(unittest.TestCase):
    def setUp(self):
        self.environ = {}

    def test_should_substitute_tilde_in_place_of_home_dir(self):
        self.environ['HOME'] = '/home/user'
        self.trash_dir = "/home/user/.local/share/Trash"
        self.assert_name_is('~/.local/share/Trash')

    def test_should_not_substitute(self):
        self.environ['HOME'] = '/home/user'
        self.environ['TRASH_PUT_DISABLE_SHRINK'] = '1'
        self.trash_dir = "/home/user/.local/share/Trash"
        self.assert_name_is('/home/user/.local/share/Trash')

    def test_when_not_in_home_dir(self):
        self.environ['HOME'] = '/home/user'
        self.trash_dir = "/not-in-home/Trash"
        self.assert_name_is('/not-in-home/Trash')

    def test_tilde_works_also_with_trailing_slash(self):
        self.environ['HOME'] = '/home/user/'
        self.trash_dir = "/home/user/.local/share/Trash"
        self.assert_name_is('~/.local/share/Trash')

    def test_str_uses_tilde_with_many_slashes(self):
        self.environ['HOME'] = '/home/user////'
        self.trash_dir = "/home/user/.local/share/Trash"
        self.assert_name_is('~/.local/share/Trash')

    def test_dont_get_confused_by_empty_home_dir(self):
        self.environ['HOME'] = ''
        self.trash_dir = "/foo/Trash"
        self.assert_name_is('/foo/Trash')

    def test_should_work_even_if_HOME_does_not_exists(self):
        self.trash_dir = "/foo/Trash"
        self.assert_name_is('/foo/Trash')

    def assert_name_is(self, expected_name):
        self.candidate = Candidate(self.trash_dir, '', '', '', None)
        shrinked = self.candidate.shrink_user(self.environ)
        assert expected_name == shrinked
