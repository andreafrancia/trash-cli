import datetime
import unittest

from trashcli.put import TrashDirectoryForPut
from trashcli.put import TopDirRelativePaths
from mock import Mock, call


class TestTrashing(unittest.TestCase):
    def setUp(self):
        self.now = lambda: datetime.datetime(1970, 1, 1)
        self.fs = Mock()
        path_maker = TopDirRelativePaths('/')
        self.info_dir = Mock(['persist_trash_info'])
        self.info_dir.persist_trash_info.return_value = 'info_file'
        self.trashdir = TrashDirectoryForPut('~/.Trash', '/', self.fs,
                                             path_maker, self.info_dir)
        path_maker = Mock()
        path_maker.calc_parent_path.return_value = ''
        self.trashdir.path_maker = path_maker

    def test_the_file_should_be_moved_in_trash_dir(self):

        self.trashdir.trash2('foo', self.now)

        assert self.fs.mock_calls == [call.move('foo', 'files/')]
        assert self.info_dir.mock_calls == [
            call.persist_trash_info(
                'foo',
                b'[Trash Info]\nPath=foo\nDeletionDate=1970-01-01T00:00:00\n')]

    def test_should_rollback_trashinfo_creation_on_problems(self):
        self.fs.move.side_effect = IOError

        try:
            self.trashdir.trash2('foo', self.now)
        except IOError:
            pass

        assert self.fs.mock_calls == [call.move('foo', 'files/'),
                                      call.remove_file('info_file')]
        assert self.info_dir.mock_calls == [
            call.persist_trash_info(
                'foo',
                b'[Trash Info]\nPath=foo\nDeletionDate=1970-01-01T00:00:00\n')]
