# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
from trashcli.parse_trashinfo.parse_path import parse_path


def test_how_to_parse_original_path():
    assert 'foo.txt' == parse_path('Path=foo.txt')
    assert '/path/to/be/escaped' == parse_path(
        'Path=%2Fpath%2Fto%2Fbe%2Fescaped')
