from trashcli.compat import TextType


def printable(text):  # type: (str) -> TextType
    text = ''.join(_escape_raw_byte(c) for c in text)
    # last resort for any other char the stream can not take
    encode_result = text.encode('utf-8', 'backslashreplace')  # type: bytes
    result = encode_result.decode('utf-8')  # type: TextType
    return result

def _escape_raw_byte(c):  # type: (str) -> str
    cp = ord(c)
    if 0xdc80 <= cp <= 0xdcff:
        # a lone surrogate stands for one raw byte, show that byte
        return '\\x%02x' % (cp - 0xdc00)
    return c
