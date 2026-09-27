import pytest

from tests.support.trashinfo.trashinfos import an_empty_trashinfo
from trashcli.parse_trashinfo.parse_original_location import OriginalLocationParser
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs


class TestTrashInfoParser:
    def test_1(self):
        parser = OriginalLocationParser(RealVolumePathFs())
        assert '/foo.txt' == parser.parse_original_location("[Trash Info]\n"
                                                            "Path=/foo.txt\n",
                                                            '/')

    def test_it_raises_error_on_parsing_original_location(self):
        parser = OriginalLocationParser(RealVolumePathFs())
        with pytest.raises(ParseError) as exc_info:
            parser.parse_original_location(an_empty_trashinfo(), '/')
        assert str(exc_info.value) == 'Unable to parse Path'
