from nose.tools import assert_equals
from trashcli.trash import TrashDirectory

class TestTrashInfoPath:
    def test_for_absolute_paths(self):
        self.dir = TrashDirectory('/volume/.Trash', '/volume')
        self.dir.store_absolute_paths()
        self.assert_path_for_trashinfo_is('/file'            , '/file')
        self.assert_path_for_trashinfo_is('/file'            , '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file'    , '/outside/file')
        self.assert_path_for_trashinfo_is('/volume/file'     , '/volume/file')
        self.assert_path_for_trashinfo_is('/volume/dir/file' , '/volume/dir/file')

    def test_for_relative_paths(self):
        self.dir = TrashDirectory('/volume/.Trash', '/volume')
        self.dir.store_relative_paths()
        self.assert_path_for_trashinfo_is('/file'         , '/file')
        self.assert_path_for_trashinfo_is('/file'         , '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file' , '/outside/file')
        self.assert_path_for_trashinfo_is('file'          , '/volume/file')
        self.assert_path_for_trashinfo_is('dir/file'      , '/volume/dir/file')

    def assert_path_for_trashinfo_is(self, expected_value, file_to_be_trashed):
        result = self.dir._path_for_trashinfo(file_to_be_trashed)
        assert_equals(expected_value, result)
