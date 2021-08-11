import unittest

from mock import Mock, call

from trashcli.empty import Guard, NoGuard
from trashcli.trash import trash_dir_found


def prepare_output_message(trash_dirs):
    result = []
    if trash_dirs:
        result.append("Would empty the following trash directories:")
        for event, args in trash_dirs:
            if event == trash_dir_found:
                trash_dir, volume = args
                result.append("    - %s" % trash_dir)
        result.append("")
        return "\n".join(result)
    else:
        return 'No trash directories to empty.\n'


class Test(unittest.TestCase):
    def test_one_dir(self):
        trash_dirs = [
            (trash_dir_found, ('/Trash', '/')),
        ]
        result = prepare_output_message(trash_dirs)

        assert """\
Would empty the following trash directories:
    - /Trash
""" == result

    def test_multiple_dirs(self):
        trash_dirs = [
            (trash_dir_found, ('/Trash1', '/')),
            (trash_dir_found, ('/Trash2', '/')),
        ]
        result = prepare_output_message(trash_dirs)

        assert """\
Would empty the following trash directories:
    - /Trash1
    - /Trash2
""" == result

    def test_no_dirs(self):
        trash_dirs = []

        result = prepare_output_message(trash_dirs)

        assert """\
No trash directories to empty.
""" == result


class TestGuard(unittest.TestCase):
    def setUp(self):
        self.user = Mock(spec=['do_you_wanna_empty_trash_dirs'])
        self.emptier = Mock(spec=['do_empty'])
        self.guard = Guard()

    def test_user_says_yes(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = True

        self.guard.ask_the_user(self.user, ['trash_dirs'], self.emptier)

        assert {'input': [call.do_you_wanna_empty_trash_dirs(['trash_dirs'])],
                'emptier': [call.do_empty(['trash_dirs'])]} == \
               {'input': self.user.mock_calls,
                'emptier': self.emptier.mock_calls}

    def test_user_says_no(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = False

        self.guard.ask_the_user(self.user, ['trash_dirs'], self.emptier)

        assert {'input': [call.do_you_wanna_empty_trash_dirs(['trash_dirs'])],
                'emptier': []} == \
               {'input': self.user.mock_calls,
                'emptier': self.emptier.mock_calls}


class TestNoGuard(unittest.TestCase):
    def setUp(self):
        self.user = Mock(spec=[])
        self.emptier = Mock(spec=['do_empty'])
        self.guard = NoGuard()

    def test_it_just_calls_the_emptier(self):

        self.guard.ask_the_user(self.user, ['trash_dirs'], self.emptier)

        assert [call.do_empty(['trash_dirs'])] == self.emptier.mock_calls
