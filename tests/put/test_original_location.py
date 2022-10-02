import unittest

from trashcli.put.original_location import OriginalLocation, parent_realpath
from trashcli.put.path_maker import PathMaker, PathMakerType


class TestOriginalLocation(unittest.TestCase):

    def setUp(self):
        self.original_location = OriginalLocation(parent_realpath, PathMaker())

    def test_for_absolute_paths(self):
        self.path_maker_type = PathMakerType.absolute_paths

        self.assert_path_for_trashinfo_is('/file', '/file')
        self.assert_path_for_trashinfo_is('/file', '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file', '/outside/file')
        self.assert_path_for_trashinfo_is('/volume/file', '/volume/file')
        self.assert_path_for_trashinfo_is('/volume/dir/file',
                                          '/volume/dir/file')

    def test_for_relative_paths(self):
        self.path_maker_type = PathMakerType.relative_paths

        self.assert_path_for_trashinfo_is('/file', '/file')
        self.assert_path_for_trashinfo_is('/file', '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file', '/outside/file')
        self.assert_path_for_trashinfo_is('file', '/volume/file')
        self.assert_path_for_trashinfo_is('dir/file', '/volume/dir/file')

    def assert_path_for_trashinfo_is(self, expected_value, file_to_be_trashed):
        result = self.original_location.for_file(file_to_be_trashed,
                                                     self.path_maker_type,
                                                     '/volume')
        assert expected_value == result
