from trashcli.trash import Parser

# Try Python 3 import; if ImportError occurs, use Python 2 import
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from nose.tools import istest

@istest
class describe_Parser():
    @istest
    def it_calls_the_actions_passing_the_program_name(self):
        on_raw = MagicMock()
        parser = Parser()
        parser.add_option('raw', on_raw)

        parser(['trash-list', '--raw'])

        on_raw.assert_called_with('trash-list')

    @istest
    def how_getopt_works_with_an_invalid_option(self):
        invalid_option_callback = MagicMock()
        parser = Parser()
        parser.on_invalid_option(invalid_option_callback)

        parser(['command-name', '-x'])

        invalid_option_callback.assert_called_with('command-name', 'x')
