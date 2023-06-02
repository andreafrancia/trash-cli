import unittest

from parameterized import parameterized  # type: ignore

from tests.test_put.support.fake_fs_with_realpath import FakeFsWithRealpath
from trashcli.put.fs.parent_realpath import ParentRealpath
from trashcli.put.original_location import OriginalLocation
from trashcli.put.path_maker import PathMaker, AbsolutePaths, RelativePaths


class TestOriginalLocation(unittest.TestCase):

    def setUp(self):
        self.original_location = OriginalLocation(
            ParentRealpath(FakeFsWithRealpath()), PathMaker())

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
