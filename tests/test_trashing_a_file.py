import datetime
import unittest

from trashcli.put.parent_path import parent_path

from trashcli.put.original_location import OriginalLocation
from trashcli.put.path_maker import PathMakerType
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from mock import Mock, call


class TestTrashing(unittest.TestCase):
    def setUp(self):
        self.now = lambda: datetime.datetime(1970, 1, 1)
        self.fs = Mock()
        self.info_dir = Mock(['persist_trash_info'])
        self.info_dir.persist_trash_info.return_value = 'info_file'
        original_location = OriginalLocation(parent_path)
        path_maker = Mock()
        self.trashdir = TrashDirectoryForPut(self.fs, path_maker, self.info_dir,
                                             original_location)
        path_maker.calc_parent_path.return_value = ''

    def test_the_file_should_be_moved_in_trash_dir(self):

        self.trashdir.trash2('foo', self.now, 'trash-put', 99,
                             PathMakerType.absolute_paths, '/disk', '/info_dir')

        assert self.fs.mock_calls == [call.move('foo', 'files/')]
        assert self.info_dir.mock_calls == [
            call.persist_trash_info(
                'foo',
                b'[Trash Info]\nPath=foo\nDeletionDate=1970-01-01T00:00:00\n',
                'trash-put', 99, '/info_dir')]

    def test_should_rollback_trashinfo_creation_on_problems(self):
        self.fs.move.side_effect = IOError

        try:
            self.trashdir.trash2('foo', self.now, 'trash-put', 99,
                                 PathMakerType.absolute_paths, '/disk',
                                 '/info_dir')
        except IOError:
            pass

        assert self.fs.mock_calls == [call.move('foo', 'files/'),
                                      call.remove_file('info_file')]
        assert self.info_dir.mock_calls == [
            call.persist_trash_info(
                'foo',
                b'[Trash Info]\nPath=foo\nDeletionDate=1970-01-01T00:00:00\n',
                'trash-put', 99, '/info_dir')]
