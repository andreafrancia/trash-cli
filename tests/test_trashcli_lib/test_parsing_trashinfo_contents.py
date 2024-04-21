# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest
from datetime import datetime

from mock import MagicMock

from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parse_trashinfo import ParseTrashInfo
from trashcli.parse_trashinfo.maybe_parse_deletion_date import \
    maybe_parse_deletion_date, unknown_date
from trashcli.parse_trashinfo.parse_original_location import \
    parse_original_location
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date


class TestParseTrashInfo(unittest.TestCase):
    def test_it_should_parse_date(self):
        out = MagicMock()
        parser = ParseTrashInfo(on_deletion_date=out)

        parser.parse_trashinfo('[Trash Info]\n'
                               'Path=foo\n'
                               'DeletionDate=1970-01-01T00:00:00\n')

        out.assert_called_with(datetime(1970, 1, 1, 0, 0, 0))

    def test_it_should_parse_path(self):
        out = MagicMock()
        parser = ParseTrashInfo(on_path=out)

        parser.parse_trashinfo('[Trash Info]\n'
                               'Path=foo\n'
                               'DeletionDate=1970-01-01T00:00:00\n')

        out.assert_called_with('foo')


class TestParseDeletionDate(unittest.TestCase):
    def test1(self):
        assert parse_deletion_date('DeletionDate=2000-12-31T23:59:58') == \
               datetime(2000, 12, 31, 23, 59, 58)

    def test2(self):
        assert parse_deletion_date('DeletionDate=2000-12-31T23:59:58\n') == \
               datetime(2000, 12, 31, 23, 59, 58)

    def test3(self):
        assert parse_deletion_date(
            '[Trash Info]\nDeletionDate=2000-12-31T23:59:58') == \
               datetime(2000, 12, 31, 23, 59, 58)

    def test_two_deletion_dates(self):
        assert parse_deletion_date('DeletionDate=2000-01-01T00:00:00\n'
                                   'DeletionDate=2000-12-31T00:00:00\n') == \
               datetime(2000, 1, 1, 0, 0)


class Test_maybe_parse_deletion_date(unittest.TestCase):
    def test_on_trashinfo_without_date_parse_to_unknown_date(self):
        assert (unknown_date ==
                maybe_parse_deletion_date(a_trashinfo_without_deletion_date()))

    def test_on_trashinfo_with_date_parse_to_date(self):
        from datetime import datetime
        example_date_as_string = '2001-01-01T00:00:00'
        same_date_as_datetime = datetime(2001, 1, 1)
        assert (same_date_as_datetime ==
                maybe_parse_deletion_date(
                    make_trashinfo(example_date_as_string)))

    def test_on_trashinfo_with_invalid_date_parse_to_unknown_date(self):
        invalid_date = 'A long time ago'
        assert (unknown_date ==
                maybe_parse_deletion_date(make_trashinfo(invalid_date)))


def test_how_to_parse_original_path():
    assert 'foo.txt' == parse_path('Path=foo.txt')
    assert '/path/to/be/escaped' == parse_path(
        'Path=%2Fpath%2Fto%2Fbe%2Fescaped')


class TestTrashInfoParser(unittest.TestCase):
    def test_1(self):
        assert '/foo.txt' == parse_original_location("[Trash Info]\n"
                                                     "Path=/foo.txt\n",
                                                     '/')

    def test_it_raises_error_on_parsing_original_location(self):
        with self.assertRaises(ParseError):
            parse_original_location(an_empty_trashinfo(), '/')


def a_trashinfo_without_deletion_date():
    return ("[Trash Info]\n"
            "Path=foo.txt\n")


def make_trashinfo(date):
    return ("[Trash Info]\n"
            "Path=foo.txt\n"
            "DeletionDate=%s" % date)


def an_empty_trashinfo():
    return ''
