import six

from typing import TextIO

from trashcli.compat import TextType, fsdecode_text


def printable(text):  # type: (str) -> TextType
    text = fsdecode_text(text)
    text = ''.join(_escape_raw_byte(text, i) for i in range(len(text)))
    # last resort for any other char the stream can not take
    encode_result = text.encode('utf-8', 'backslashreplace')  # type: bytes
    result = encode_result.decode('utf-8')  # type: TextType
    return result


def write_text(stream, text):  # type: (TextIO, TextType) -> None
    text = fsdecode_text(text)
    if six.PY2:
        # Python 2 writes unicode to a byte stream by encoding with the
        # default encoding, which raises for non-ASCII when redirected.
        encoding = getattr(stream, 'encoding', None) or 'ascii'
        stream.write(text.encode(encoding, 'backslashreplace') + b'\n')
    else:
        encoding = getattr(stream, 'encoding', None)
        if encoding:
            text = text.encode(encoding, 'backslashreplace').decode(encoding)
        stream.write(text + u'\n')


def _escape_raw_byte(text, index):  # type: (str, int) -> str
    cp = ord(text[index])
    if 0xdc80 <= cp <= 0xdcff:
        if index > 0 and 0xd800 <= ord(text[index - 1]) <= 0xdbff:
            return text[index]
        # a lone surrogate stands for one raw byte, show that byte
        return '\\x%02x' % (cp - 0xdc00)
    return text[index]
