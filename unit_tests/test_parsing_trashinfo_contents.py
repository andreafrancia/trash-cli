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

class TestParsing:
    def test_1(self):
        parser = LazyTrashInfoParser(lambda:("[TrashInfo]\n"
                                             "Path=/foo.txt\n"), volume_path = '/')
        assert_equals('/foo.txt', parser.original_location())

class TestLazyTrashInfoParser_with_empty_trashinfo:
    def setUp(self):
        self.parser = LazyTrashInfoParser(contents=an_empty_trashinfo, volume_path='/')

    def test_it_raises_error_on_parsing_original_location(self):
        with assert_raises(ParseError):
            self.parser.original_location()

    #def test_it_raises_error_on_parsing_deletion_date(self):
    #    with assert_raises(ParseError):
    #        self.parser.deletion_date()

def a_valid_trashinfo():
    return ("[TrashInfo]\n"
            "Path=foo.txt\n"
            "DeletionDate=2000-12-31T23:59:58")
def an_empty_trashinfo():
    return ''



