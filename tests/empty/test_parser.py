import unittest

from trashcli.empty import Parser
from mock import call, Mock


class TestParser(unittest.TestCase):
    def setUp(self):
        self.on_help = Mock()
        self.on_version = Mock()
        self.on_argument = Mock()
        self.on_default = Mock()
        self.on_invalid_option = Mock()
        self.on_trash_dir = Mock()

        self.parser = Parser(
            on_help=self.on_help,
            on_version=self.on_version,
            on_invalid_option=self.on_invalid_option,
            on_trash_dir=self.on_trash_dir,
            on_argument=self.on_argument,
            on_default=self.on_default,
        )

    def all_calls(self):
        return {
            'on_help': self.on_help.mock_calls,
            'on_version': self.on_version.mock_calls,
            'on_argument': self.on_argument.mock_calls,
            'on_default': self.on_default.mock_calls,
            'on_invalid_option': self.on_invalid_option.mock_calls,
            'on_trash_dir': self.on_trash_dir.mock_calls,
        }

    def test_argument_option_called_without_argument(self):
        self.my_parse_args(['--trash-dir'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [],
                'on_invalid_option': [call('trash-empty', 'trash-dir')],
                'on_trash_dir': [],
                'on_version': []}

    def test_argument_option_called_with_argument(self):
        self.my_parse_args(['--trash-dir', 'arg'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [],
                'on_invalid_option': [],
                'on_trash_dir': [call('arg')],
                'on_version': []}

    def test_argument_option_called_with_argument2(self):
        self.my_parse_args(['--trash-dir=arg'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [],
                'on_invalid_option': [],
                'on_trash_dir': [call('arg')],
                'on_version': []}

    def test_argument_option_called_with_argument3(self):
        self.my_parse_args(['--trash-dir', 'arg'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [],
                'on_invalid_option': [],
                'on_trash_dir': [call('arg')],
                'on_version': []}

    def test_it_calls_help(self):
        self.my_parse_args(['--help'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [call('trash-empty')],
                'on_invalid_option': [],
                'on_trash_dir': [],
                'on_version': []}

    def test_how_getopt_works_with_an_invalid_option(self):
        self.my_parse_args(['-x'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [],
                'on_invalid_option': [call('trash-empty', 'x')],
                'on_trash_dir': [],
                'on_version': []}

    def test_on_argument(self):
        self.my_parse_args(['1'])

        assert self.all_calls() == \
               {'on_argument': [call('1')],
                'on_default': [call()],
                'on_help': [],
                'on_invalid_option': [],
                'on_trash_dir': [],
                'on_version': []}

    def test_on_help(self):
        self.my_parse_args(['--help'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [call('trash-empty')],
                'on_invalid_option': [],
                'on_trash_dir': [],
                'on_version': []}

    def test_trash_dir_multiple_days(self):
        self.my_parse_args(['--trash-dir', 'one',
                            '--trash-dir', 'two'])

        assert self.all_calls() == \
               {'on_argument': [],
                'on_default': [],
                'on_help': [],
                'on_invalid_option': [],
                'on_trash_dir': [call('one')],
                'on_version': []}

    def my_parse_args(self, args):
        self.parser.parse_argv(['trash-empty'] + args)
