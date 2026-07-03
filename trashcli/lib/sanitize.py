from __future__ import absolute_import

import os

REPLACEMENT = u'\ufffd'


def sanitize_for_output(s):
    if s is None:
        return s
    chars = list(s)
    out = []
    for i, c in enumerate(chars):
        cp = ord(c)
        if cp == 0x09 or cp == 0x0A:
            out.append(c)
        elif cp == 0x0D:
            # A carriage return is safe only when it is the CR of a CRLF pair.
            out.append(c if i + 1 < len(chars) and chars[i + 1] == u'\n' else REPLACEMENT)
        elif cp < 0x20 or cp == 0x7F or 0x80 <= cp <= 0x9F or 0xDC80 <= cp <= 0xDCFF:
            out.append(REPLACEMENT)
        else:
            out.append(c)
    return u''.join(out)


def sanitize_for_stream(s, stream):
    return sanitize_for_output(s) if filtering_enabled(stream) else s


def filtering_enabled(stream):
    if os.environ.get('TRASH_RAW_OUTPUT'):
        return False
    try:
        return bool(stream.isatty())
    except Exception:
        return False
