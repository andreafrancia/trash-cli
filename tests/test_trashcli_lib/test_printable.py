import unittest

from trashcli.compat import fsdecode
from trashcli.lib.printable import printable


class TestPrintable(unittest.TestCase):
    def test_plain_text_is_unchanged(self):
        assert printable('/foo/bar baz') == '/foo/bar baz'

    def test_valid_non_ascii_text_is_unchanged(self):
        assert printable(u'/foo/caf\xe9') == u'/foo/caf\xe9'

    def test_raw_bytes_are_shown_as_escapes(self):
        assert printable(fsdecode(b'bad\xffname')) == 'bad\\xffname'
