from __future__ import absolute_import

import os
import sys

from six import binary_type
from six import text_type

try:
    from urllib.parse import quote_from_bytes
    from urllib.parse import unquote_to_bytes
except ImportError:
    from urllib import quote as _quote
    from urllib import unquote as _unquote

    def quote_from_bytes(raw_path, safe='/'):
        return _quote(raw_path, safe)

    def unquote_to_bytes(quoted_path):
        return _unquote(_fsencode(quoted_path))


def quote_trashinfo_path(path):
    return quote_from_bytes(_fsencode(path), safe='/')


def unquote_trashinfo_path(value):
    return _fsdecode(unquote_to_bytes(value))


def _fsencode(path):
    if hasattr(os, 'fsencode'):
        return os.fsencode(path)
    if isinstance(path, binary_type):
        return path
    if isinstance(path, text_type):
        return path.encode(_filesystem_encoding())
    return path


def _fsdecode(path):
    if hasattr(os, 'fsdecode'):
        return os.fsdecode(path)
    return path


def _filesystem_encoding():
    return sys.getfilesystemencoding() or sys.getdefaultencoding()
