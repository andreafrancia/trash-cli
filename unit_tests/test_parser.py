from trashcli.trash import Parser
from mock import MagicMock, call
from nose.tools import istest, assert_equals

class TestParser():
    def setUp(self):
        self.invalid_option_callback = MagicMock()
        self.on_raw = MagicMock()
        self.on_help = MagicMock()
        self.on_option = MagicMock()

        self.parser = Parser()
        self.parser.on_invalid_option(self.invalid_option_callback)
        self.parser.add_option('raw', self.on_raw)
        self.parser.add_option('opt=', self.on_option)
        self.parser.on_help(self.on_help)

    def test_argument_option_called_without_argument(self):

        self.parser(['trash-list', '--opt'])

        assert_equals([], self.on_option.mock_calls)
        self.invalid_option_callback.assert_called_with('trash-list', 'opt')

    def test_argument_option_called_with_argument(self):

        self.parser(['trash-list', '--opt=', 'arg'])

        assert_equals([call('')], self.on_option.mock_calls)

    def test_argument_option_called_with_argument(self):

        self.parser(['trash-list', '--opt=arg'])

        assert_equals([call('arg')], self.on_option.mock_calls)

    def test_argument_option_called_with_argument(self):

        self.parser(['trash-list', '--opt', 'arg'])

        assert_equals([call('arg')], self.on_option.mock_calls)

    def test_it_calls_help(self):

        self.parser(['trash-list', '--help'])

        self.on_help.assert_called_with('trash-list')

    def test_it_calls_the_actions_passing_the_program_name(self):

        self.parser(['trash-list', '--raw'])

        self.on_raw.assert_called_with('')

    def test_how_getopt_works_with_an_invalid_option(self):

        self.parser(['command-name', '-x'])

        self.invalid_option_callback.assert_called_with('command-name', 'x')
