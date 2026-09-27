import pytest

from tests.support.trashinfo.trashinfos import an_empty_trashinfo
from trashcli.parse_trashinfo.parse_original_location import OriginalLocationParser
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs


class TestTrashInfoParser:
    def setup_method(self):
        self.parser = OriginalLocationParser(RealVolumePathFs())

    def test_1(self):
        assert '/foo.txt' == self.parser.parse_original_location(
            "[Trash Info]\n"
            "Path=/foo.txt\n",
            '/', '/.Trash-123')

    def test_it_raises_error_on_parsing_original_location(self):
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse_original_location(an_empty_trashinfo(), '/',
                                                '/.Trash-123')
        assert str(exc_info.value) == 'Unable to parse Path'

    def test_absolute_path_in_home_trash_on_a_separate_mount(self):
        assert '/home/user/foo' == self.parser.parse_original_location(
            "[Trash Info]\n"
            "Path=/home/user/foo\n",
            '/home', '/home/user/.local/share/Trash')

    def test_absolute_path_in_volume_trash_is_refused(self):
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse_original_location("[Trash Info]\n"
                                                "Path=/etc/passwd\n",
                                                '/mnt', '/mnt/.Trash-123')
        assert str(exc_info.value) == \
               'Path= must be relative for volume trashes'

    def test_absolute_path_in_shared_volume_trash_is_refused(self):
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse_original_location("[Trash Info]\n"
                                                "Path=/etc/passwd\n",
                                                '/mnt', '/mnt/.Trash/123')
        assert str(exc_info.value) == \
               'Path= must be relative for volume trashes'
