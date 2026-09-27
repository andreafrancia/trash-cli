try:
    from typing import Protocol
except ImportError as e:
    from typing_extensions import Protocol  # type: ignore[assignment]

import six

if six.PY2:
    TextType = unicode
    BytesType = bytes
else:
    TextType = str
    BytesType = bytes


def _is_high_surrogate(ch):
    return 0xD800 <= ord(ch) <= 0xDBFF


def _fsencode_fallback(filename):  # type: (TextType) -> BytesType
    import sys
    import six
    if isinstance(filename, bytes):
        return filename
    if not isinstance(filename, six.text_type):
        raise TypeError("expect bytes or str, not %s"
                        % type(filename).__name__)
    encoding = sys.getfilesystemencoding() or 'utf-8'
    # Emulate the 'surrogateescape' error handler: a lone surrogate in
    # U+DC80..U+DCFF stands for the raw byte 0x80..0xFF.
    chunks = []
    start = 0
    for i, ch in enumerate(filename):
        code = ord(ch)
        if (0xDC80 <= code <= 0xDCFF and
                not (i > 0 and _is_high_surrogate(filename[i - 1]))):
            chunks.append(filename[start:i].encode(encoding))
            chunks.append(bytes(bytearray([code - 0xDC00])))
            start = i + 1
    chunks.append(filename[start:].encode(encoding))
    return b''.join(chunks)


def _fsdecode_fallback(raw):  # type: (bytes) -> TextType
    import six
    # like python 3 os.fsdecode with utf-8: each byte that is not valid
    # utf-8 becomes the lone surrogate U+DC80..U+DCFF
    result = []
    while raw:
        try:
            result.append(raw.decode('utf-8'))
            break
        except UnicodeDecodeError as e:
            result.append(raw[:e.start].decode('utf-8'))
            result.append(six.unichr(0xdc00 + ord(raw[e.start:e.start + 1])))
            raw = raw[e.start + 1:]
    return u''.join(result)

import os
fsdecode = getattr(os, 'fsdecode', _fsdecode_fallback)
fsencode = getattr(os, 'fsencode', _fsencode_fallback)
