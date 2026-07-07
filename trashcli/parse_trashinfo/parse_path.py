from __future__ import absolute_import

import sys

from trashcli.compat import fsdecode
from trashcli.parse_trashinfo.parser_error import ParseError

if sys.version_info[0] >= 3:
    # python 3: unquote to raw bytes so no byte gets lost
    from urllib.parse import unquote_to_bytes
else:
    # python 2: plain unquote already works on byte strings
    from urllib import unquote as unquote_to_bytes


def unquote_path(quoted_path):  # type: (str) -> str
    # go through bytes so any file name comes back unchanged
    return fsdecode(unquote_to_bytes(quoted_path))


def parse_path(contents):
    for line in contents.split('\n'):
        if line.startswith('Path='):
            return unquote_path(line[len('Path='):])
    raise ParseError('Unable to parse Path')
