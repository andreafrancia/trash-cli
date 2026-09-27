from trashcli.compat import fsdecode, fsencode


class TestFsDecode:
    def test_roundtring(self):
        raw = b'caf\xe9.txt' # Latin-1 name, invalid as UTF-8
        name = fsdecode(raw)
        assert fsencode(name) == raw

    def test_fs_encode(self):
        assert fsencode(b'caf\xe9') == b'caf\xe9'  # bytes pass through
        assert fsencode(u'caf\udce9.txt') == b'caf\xe9.txt'  # escape -> raw byte
        assert fsencode(u'\udcff\udcfe') == b'\xff\xfe'  # consecutive escapes
        assert fsencode(u'caff\xe8') == u'caff\xe8'.encode('utf-8')  # normal non-ASCII
        assert fsencode(u'\U00010080') == u'\U00010080'.encode('utf-8')  # non-BMP character, stored as a pair