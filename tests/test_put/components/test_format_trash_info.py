import unittest

from trashcli.compat import fsdecode
from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.put.format_trash_info import format_original_location

# this is how a file name with the raw byte 0xff reaches python
bad_name = fsdecode(b'/foo/bad\xffname')


class TestFormatOriginalLocation(unittest.TestCase):
    def test_plain_name(self):
        assert format_original_location('/foo/bar') == '/foo/bar'

    def test_name_with_spaces(self):
        assert format_original_location('/foo/a file') == '/foo/a%20file'

    def test_name_with_a_byte_that_is_not_valid_text(self):
        assert format_original_location(bad_name) == '/foo/bad%FFname'

    def test_round_trip_keeps_the_name_unchanged(self):
        contents = 'Path=%s\n' % format_original_location(bad_name)

        assert parse_path(contents) == bad_name
