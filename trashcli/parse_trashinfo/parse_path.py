from __future__ import absolute_import

from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.trashinfo_path import unquote_trashinfo_path


def parse_path(contents):
    for line in contents.split('\n'):
        if line.startswith('Path='):
            return unquote_trashinfo_path(line[len('Path='):])
    raise ParseError('Unable to parse Path')
