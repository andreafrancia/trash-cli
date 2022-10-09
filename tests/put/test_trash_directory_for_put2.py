import datetime
import os.path
import unittest

from mock import Mock, call

from tests.put.support.dummy_clock import DummyClock
from trashcli.put.original_location import OriginalLocation
from trashcli.put.parent_realpath import ParentRealpath
from trashcli.put.path_maker import PathMakerType
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut


class TestTrashing(unittest.TestCase):
    def setUp(self):
        self.fs = Mock()
        self.info_dir = Mock(['persist_trash_info'])
        path_maker = Mock()
        parent_realpath = ParentRealpath(os.path.realpath)
        original_location = OriginalLocation(parent_realpath, path_maker)
        clock = DummyClock(datetime.datetime(1970, 1, 1))
        self.trashdir = TrashDirectoryForPut(self.fs, self.info_dir,
                                             original_location,
                                             clock)
        path_maker.calc_parent_path.return_value = ''

    def test_the_file_should_be_moved_in_trash_dir(self):
        self.info_dir.persist_trash_info.return_value = 'info_file'

        self.trashdir.trash2('foo', 'trash-put', 99,
                             PathMakerType.absolute_paths, '/disk', '/trash')

        assert self.fs.mock_calls == [call.move('foo', 'files/')]
        assert self.info_dir.mock_calls == [
            call.persist_trash_info(
                'foo',
                b'[Trash Info]\nPath=foo\nDeletionDate=1970-01-01T00:00:00\n',
                'trash-put', 99, '/trash/info')]

    def test_should_rollback_trashinfo_creation_on_problems(self):
        self.info_dir.persist_trash_info.return_value = 'info_file'
        self.fs.move.side_effect = IOError

        try:
            self.trashdir.trash2('foo', 'trash-put', 99,
                                 PathMakerType.absolute_paths, '/disk',
                                 '/trash')
        except IOError:
            pass

        assert self.fs.mock_calls == [call.move('foo', 'files/'),
                                      call.remove_file('info_file')]
        assert self.info_dir.mock_calls == [
            call.persist_trash_info(
                'foo',
                b'[Trash Info]\nPath=foo\nDeletionDate=1970-01-01T00:00:00\n',
                'trash-put', 99, '/trash/info')]
