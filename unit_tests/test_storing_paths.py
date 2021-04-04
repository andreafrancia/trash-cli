from trashcli.put import TrashDirectoryForPut
from trashcli.put import AbsolutePaths, TopDirRelativePaths
from mock import Mock


class TestHowOriginalLocationIsStored:
    def test_for_absolute_paths(self):
        fs = Mock()
        path_maker = AbsolutePaths(None)
        logger = Mock()
        self.dir = TrashDirectoryForPut('/volume/.Trash', '/volume', fs,
                                        path_maker, logger)

        self.assert_path_for_trashinfo_is('/file'            , '/file')
        self.assert_path_for_trashinfo_is('/file'            , '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file'    , '/outside/file')
        self.assert_path_for_trashinfo_is('/volume/file'     , '/volume/file')
        self.assert_path_for_trashinfo_is('/volume/dir/file' , '/volume/dir/file')

    def test_for_relative_paths(self):
        path_maker = TopDirRelativePaths('/volume')
        logger = Mock()
        self.dir = TrashDirectoryForPut('/volume/.Trash', '/volume', Mock(),
                                        path_maker, logger)

        self.assert_path_for_trashinfo_is('/file'         , '/file')
        self.assert_path_for_trashinfo_is('/file'         , '/dir/../file')
        self.assert_path_for_trashinfo_is('/outside/file' , '/outside/file')
        self.assert_path_for_trashinfo_is('file'          , '/volume/file')
        self.assert_path_for_trashinfo_is('dir/file'      , '/volume/dir/file')

    def assert_path_for_trashinfo_is(self, expected_value, file_to_be_trashed):
        result = self.dir.path_for_trash_info_for_file(file_to_be_trashed)
        assert expected_value == result
