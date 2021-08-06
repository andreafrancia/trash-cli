import unittest

from mock import Mock, call

from trashcli.empty import Guard
from trashcli.trash import trash_dir_found


def prepare_output_message(trash_dirs):
    result = []
    result.append("Would empty trash dirs:")
    for event, args in trash_dirs:
        if event == trash_dir_found:
            trash_dir, volume = args
            result.append("    - %s" % trash_dir)
    result.append("")
    return "\n".join(result)


class Test(unittest.TestCase):
    def test_one_dir(self):
        trash_dirs = [
            (trash_dir_found, ('/Trash', '/')),
                      ]
        result = prepare_output_message(trash_dirs)

        assert """\
Would empty trash dirs:
    - /Trash
""" == result


class TestGuard(unittest.TestCase):
    def setUp(self):
        self.user = Mock(spec=['do_you_wanna_empty_trash_dirs'])
        self.emptier = Mock(spec=['do_empty'])
        self.guard = Guard(self.emptier)

    def test_user_says_yes(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = True

        self.guard.ask_the_user(self.user, ['trash_dirs'])

        assert {'input': [call.do_you_wanna_empty_trash_dirs(['trash_dirs'])],
                'emptier': [call(['trash_dirs'])]} == \
               {'input': self.user.mock_calls,
                'emptier': self.emptier.mock_calls}

    def test_user_says_no(self):
        self.user.do_you_wanna_empty_trash_dirs.return_value = False

        self.guard.ask_the_user(self.user, ['trash_dirs'])

        assert {'input': [call.do_you_wanna_empty_trash_dirs(['trash_dirs'])],
                'emptier': []} == \
               {'input': self.user.mock_calls,
                'emptier': self.emptier.mock_calls}
