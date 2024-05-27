from __future__ import absolute_import

from six import binary_type
from six.moves.urllib.parse import unquote

from trashcli.parse_trashinfo.parser_error import ParseError


def parse_path(contents,  # type: binary_type
               ): # type: (...) -> str
    for line in contents.split(b'\n'):
        if line.startswith(b'Path='):
            return unquote(line[len(b'Path='):])
    raise ParseError('Unable to parse Path')
