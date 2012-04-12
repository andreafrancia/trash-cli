from trashcli.trash import Parser
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
