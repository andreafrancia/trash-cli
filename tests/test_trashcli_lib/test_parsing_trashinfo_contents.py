# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest
from datetime import datetime

from tests.support.py2mock import MagicMock

from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parse_trashinfo import ParseTrashInfo
from trashcli.parse_trashinfo.maybe_parse_deletion_date import \
    maybe_parse_deletion_date, unknown_date
from trashcli.parse_trashinfo.parse_original_location import \
    parse_original_location
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date


class TestParseTrashInfo:
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


def test_how_to_parse_original_path():
    assert 'foo.txt' == parse_path('Path=foo.txt')
    assert '/path/to/be/escaped' == parse_path(
        'Path=%2Fpath%2Fto%2Fbe%2Fescaped')


def a_trashinfo_without_deletion_date():
    return ("[Trash Info]\n"
            "Path=foo.txt\n")


def make_trashinfo(date):
    return ("[Trash Info]\n"
            "Path=foo.txt\n"
            "DeletionDate=%s" % date)


