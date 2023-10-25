import os
import unittest

from parameterized import parameterized  # type: ignore

from tests.test_put.support.fake_fs.fake_fs import FakeFs
from trashcli.put.core.path_maker_type import PathMakerType
from trashcli.put.original_location import OriginalLocation

AbsolutePaths = PathMakerType.AbsolutePaths
RelativePaths = PathMakerType.RelativePaths


class TestOriginalLocation(unittest.TestCase):

    def setUp(self):
        self.original_location = OriginalLocation(FakeFsWithRealpath())

    @parameterized.expand([
        ('/volume', '/file', AbsolutePaths, '/file',),
        ('/volume', '/file/././', AbsolutePaths, '/file',),
        ('/volume', '/dir/../file', AbsolutePaths, '/file'),
        ('/volume', '/dir/../././file', AbsolutePaths, '/file'),
        ('/volume', '/outside/file', AbsolutePaths, '/outside/file'),
        ('/volume', '/volume/file', AbsolutePaths, '/volume/file',),
        ('/volume', '/volume/dir/file', AbsolutePaths, '/volume/dir/file'),
        ('/volume', '/file', RelativePaths, '/file'),
        ('/volume', '/dir/../file', RelativePaths, '/file'),
        ('/volume', '/outside/file', RelativePaths, '/outside/file'),
        ('/volume', '/volume/file', RelativePaths, 'file'),
        ('/volume', '/volume/dir/file', RelativePaths, 'dir/file'),
    ])
    def test_original_location(self, volume, file_to_be_trashed, path_type,
                               expected_result):
        result = self.original_location.for_file(file_to_be_trashed, path_type,
                                                 volume)
        assert expected_result == result


class FakeFsWithRealpath(FakeFs):
    def parent_realpath2(self, path):
        return os.path.dirname(path)
