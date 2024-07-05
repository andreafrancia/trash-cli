import unittest

from tests.support.mock import Mock, call
from trashcli.empty.guard import Guard, UserIntention


class TestGuard(unittest.TestCase):
    def setUp(self):
        self.user = Mock(spec=['do_you_wanna_empty_trash_dirs'])
        self.guard = Guard(self.user)

    def test_user_says_yes(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = True

        result = self.guard.ask_the_user(True, ['trash_dirs'])

        assert UserIntention(ok_to_empty=True,
                             trash_dirs=['trash_dirs']) == result

    def test_user_says_no(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = False

        result = self.guard.ask_the_user(True, ['trash_dirs'])

        assert UserIntention(ok_to_empty=False,
                             trash_dirs=[]) == result

    def test_it_just_calls_the_emptier(self):
        result = self.guard.ask_the_user(False, ['trash_dirs'])

        assert UserIntention(ok_to_empty=True,
                             trash_dirs=['trash_dirs']) == result
