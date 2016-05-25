from trashcli.put import TrashDirectoryForPut
from nose.tools import assert_equal

# Try Python 3 import; if ImportError occurs, use Python 2 import
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

class TestHowOriginalLocationIsStored:
    def test_for_absolute_paths(self):
        fs = Mock()
        self.dir = TrashDirectoryForPut('/volume/.Trash', '/volume', fs = fs)
        self.dir.store_absolute_paths()

        self.assert_path_for_trashinfo_is('/file'            , '/file')
        self.assert_path_for_trashinfo_is('/file'            , '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file'    , '/outside/file')
        self.assert_path_for_trashinfo_is('/volume/file'     , '/volume/file')
        self.assert_path_for_trashinfo_is('/volume/dir/file' , '/volume/dir/file')

    def test_for_relative_paths(self):
        self.dir = TrashDirectoryForPut('/volume/.Trash', '/volume')
        self.dir.store_relative_paths()

        self.assert_path_for_trashinfo_is('/file'         , '/file')
        self.assert_path_for_trashinfo_is('/file'         , '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file' , '/outside/file')
        self.assert_path_for_trashinfo_is('file'          , '/volume/file')
        self.assert_path_for_trashinfo_is('dir/file'      , '/volume/dir/file')

    def assert_path_for_trashinfo_is(self, expected_value, file_to_be_trashed):
        result = self.dir.path_for_trash_info.for_file(file_to_be_trashed)
        assert_equal(expected_value, result)
