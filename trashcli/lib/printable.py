def printable(text):  # type: (str) -> str
    # make a text safe to print on any terminal
    if isinstance(text, bytes):
        # python 2 byte strings go out unchanged
        return text
    try:
        text.encode('utf-8')
        return text
    except UnicodeEncodeError:
        text = ''.join(_escape_raw_byte(c) for c in text)
        # last resort for any other char the stream can not take
        return text.encode('utf-8', 'backslashreplace').decode('utf-8')


def _escape_raw_byte(c):  # type: (str) -> str
    cp = ord(c)
    if 0xdc80 <= cp <= 0xdcff:
        # a lone surrogate stands for one raw byte, show that byte
        return '\\x%02x' % (cp - 0xdc00)
    return c
