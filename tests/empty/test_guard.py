import unittest

from mock import Mock, call

from trashcli.empty import Guard, NoGuard


class TestGuard(unittest.TestCase):
    def setUp(self):
        self.user = Mock(spec=['do_you_wanna_empty_trash_dirs'])
        self.emptier = Mock(spec=['do_empty'])
        self.guard = Guard()

    def test_user_says_yes(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = True

        self.guard.ask_the_user(self.user, ['trash_dirs'], self.emptier)

        assert {'user': [call.do_you_wanna_empty_trash_dirs(['trash_dirs'])],
                'emptier': [call.do_empty(['trash_dirs'])]} == \
               {'user': self.user.mock_calls,
                'emptier': self.emptier.mock_calls}

    def test_user_says_no(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = False

        self.guard.ask_the_user(self.user, ['trash_dirs'], self.emptier)

        assert {'user': [call.do_you_wanna_empty_trash_dirs(['trash_dirs'])],
                'emptier': []} == \
               {'user': self.user.mock_calls,
                'emptier': self.emptier.mock_calls}


class TestNoGuard(unittest.TestCase):
    def setUp(self):
        self.user = Mock(spec=[])
        self.emptier = Mock(spec=['do_empty'])
        self.guard = NoGuard()

    def test_it_just_calls_the_emptier(self):

        self.guard.ask_the_user(self.user, ['trash_dirs'], self.emptier)

        assert [call.do_empty(['trash_dirs'])] == self.emptier.mock_calls
