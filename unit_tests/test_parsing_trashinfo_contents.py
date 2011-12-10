from nose.tools import assert_equals, assert_raises

from trashcli.trash2 import parse_deletion_date
from trashcli.trash2 import parse_path

def test_how_to_parse_date_from_trashinfo():
    from datetime import datetime
    assert_equals(datetime(2000,12,31,23,59,58), parse_deletion_date('DeletionDate=2000-12-31T23:59:58'))
    assert_equals(datetime(2000,12,31,23,59,58), parse_deletion_date('DeletionDate=2000-12-31T23:59:58\n'))
    assert_equals(datetime(2000,12,31,23,59,58), parse_deletion_date('[TrashInfo]\nDeletionDate=2000-12-31T23:59:58'))


def test_how_to_parse_original_path():
    assert_equals('foo.txt',             parse_path('Path=foo.txt'))
    assert_equals('/path/to/be/escaped', parse_path('Path=%2Fpath%2Fto%2Fbe%2Fescaped'))


from trashcli.trash2 import LazyTrashInfoParser, ParseError
class TestLazyTrashInfoParser_with_empty_trashinfo:
    def setUp(self):
        self.parser = LazyTrashInfoParser(contents=lambda:'', volume_path='/')

    def test_it_raises_error_on_parsing_original_location(self):
        with assert_raises(ParseError):
            self.parser.original_location()

    #def test_it_raises_error_on_parsing_deletion_date(self):
    #    with assert_raises(ParseError):
    #        self.parser.deletion_date()

from trashcli.trash2 import parse
import fudge

class TestTrashInfoParser:
    @fudge.test
    def test_it_should_signal_errors_on_empty_contents(self):
        on_error = (fudge.Fake('on_error')
                         .is_callable()
                         .expects_call().with_args('Unable to parse Path'))
        on_parse = fudge.Fake('on_parse')
        parse(an_empty_trashinfo, '/', on_parse, on_error)

    def test_it_should_call_action_on_correctly_parsed_contents(self):
        on_error = fudge.Fake("on_error")
        on_parse = fudge.Fake('on_parse').is_callable().expects_call()
        parse(a_valid_trashinfo, '/', on_parse, on_error)

def a_valid_trashinfo():
    return ("[TrashInfo]\n"
            "Path=foo.txt\n"
            "DeletionDate=2000-12-31T23:59:58")
def an_empty_trashinfo():
    return ''



