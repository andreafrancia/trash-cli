# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest

from datetime import datetime
from mock import MagicMock

from trashcli.trash import ParseTrashInfo


class Test_describe_ParseTrashInfo2(unittest.TestCase):
    def test_it_should_parse_date(self):
        out = MagicMock()
        parser = ParseTrashInfo(on_deletion_date = out)

        parser.parse_trashinfo('[Trash Info]\n'
                               'Path=foo\n'
                               'DeletionDate=1970-01-01T00:00:00\n')
        
        out.assert_called_with(datetime(1970,1,1,0,0,0))

    def test_it_should_parse_path(self):
        out = MagicMock()
        parser = ParseTrashInfo(on_path = out)

        parser.parse_trashinfo('[Trash Info]\n'
                               'Path=foo\n'
                               'DeletionDate=1970-01-01T00:00:00\n')

        out.assert_called_with('foo')

from trashcli.trash import parse_deletion_date
from trashcli.trash import parse_path

def test_how_to_parse_date_from_trashinfo():
    from datetime import datetime
    assert datetime(2000,12,31,23,59,58) == parse_deletion_date('DeletionDate=2000-12-31T23:59:58')
    assert datetime(2000,12,31,23,59,58) == parse_deletion_date('DeletionDate=2000-12-31T23:59:58\n')
    assert datetime(2000,12,31,23,59,58) == parse_deletion_date('[Trash Info]\nDeletionDate=2000-12-31T23:59:58')

from trashcli.trash import maybe_parse_deletion_date

UNKNOWN_DATE='????-??-?? ??:??:??'


class Test_describe_maybe_parse_deletion_date(unittest.TestCase):
    def test_on_trashinfo_without_date_parse_to_unknown_date(self):
        assert (UNKNOWN_DATE ==
                      maybe_parse_deletion_date(a_trashinfo_without_deletion_date()))

    def test_on_trashinfo_with_date_parse_to_date(self):
        from datetime import datetime
        example_date_as_string='2001-01-01T00:00:00'
        same_date_as_datetime=datetime(2001,1,1)
        assert (same_date_as_datetime ==
                      maybe_parse_deletion_date(make_trashinfo(example_date_as_string)))

    def test_on_trashinfo_with_invalid_date_parse_to_unknown_date(self):
        invalid_date='A long time ago'
        assert (UNKNOWN_DATE ==
                      maybe_parse_deletion_date(make_trashinfo(invalid_date)))

def test_how_to_parse_original_path():
    assert 'foo.txt' ==             parse_path('Path=foo.txt')
    assert '/path/to/be/escaped' == parse_path('Path=%2Fpath%2Fto%2Fbe%2Fescaped')


from trashcli.restore import TrashInfoParser
from trashcli.trash import ParseError

class TestParsing(unittest.TestCase):
    def test_1(self):
        parser = TrashInfoParser("[Trash Info]\n"
                                 "Path=/foo.txt\n", volume_path = '/')
        assert '/foo.txt' == parser.original_location()

class TestTrashInfoParser_with_empty_trashinfo(unittest.TestCase):
    def setUp(self):
        self.parser = TrashInfoParser(contents=an_empty_trashinfo(),
                                      volume_path='/')

    def test_it_raises_error_on_parsing_original_location(self):
        with self.assertRaises(ParseError):
            self.parser.original_location()

def a_trashinfo_without_deletion_date():
    return ("[Trash Info]\n"
            "Path=foo.txt\n")

def make_trashinfo(date):
    return ("[Trash Info]\n"
            "Path=foo.txt\n"
            "DeletionDate=%s" % date)
def an_empty_trashinfo():
    return ''
