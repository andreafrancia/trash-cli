import unittest

import pytest

from trashcli.compat import fsdecode
from trashcli.lib.printable import printable


class TestPrintable(unittest.TestCase):
    def test_plain_text_is_unchanged(self):
        assert printable('/foo/bar baz') == '/foo/bar baz'

    def test_valid_non_ascii_text_is_unchanged(self):
        assert printable(u'/foo/caf\xe9') == u'/foo/caf\xe9'

    @property
    def _badname(self):
        return b'bad\xffname'

    def test_badname_is_invalid(self):
        # this can be checked only in python 2.7
        with pytest.raises(UnicodeDecodeError) as excinfo:
            self._badname.decode('utf-8')

        norm_exc_msg = str(excinfo.value).replace('utf8', 'utf-8') # needed for python 2.7
        assert norm_exc_msg == "'utf-8' codec can't decode byte 0xff in position 3: invalid start byte"

    def test_fsdecode_uses_surrogate(self):
        assert fsdecode(b'bad\xffname') == u'bad\udcffname'

    def test_raw_bytes_are_shown_as_escapes(self):
        not_valid_utf8_name = fsdecode(b'bad\xffname')
        assert printable(not_valid_utf8_name) == 'bad\\xffname'
