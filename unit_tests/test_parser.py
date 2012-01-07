from trashcli.trash import Parser
from dingus import Dingus

def test_parser():
    on_raw = Dingus()
    parser = Parser()
    parser.add_option('raw', on_raw)

    parser(['trash-list', '--raw'])

    assert on_raw.calls('()')
