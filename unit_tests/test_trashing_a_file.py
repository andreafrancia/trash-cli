import unittest

from trashcli.put import TrashDirectoryForPut
from trashcli.put import TopDirRelativePaths
from mock import Mock
from mock import ANY

class TestTrashing(unittest.TestCase):
    def setUp(self):
        self.now = Mock()
        self.fs = Mock()
        path_maker = TopDirRelativePaths('/')
        self.logger = Mock(['debug'])
        self.trashdir = TrashDirectoryForPut('~/.Trash', '/', self.fs,
                                             path_maker, self.logger)
        path_maker = Mock()
        path_maker.calc_parent_path.return_value = ''
        self.trashdir.path_maker = path_maker

    def test_the_file_should_be_moved_in_trash_dir(self):

        self.trashdir.trash2('foo', self.now)

        self.fs.move.assert_called_with('foo', '~/.Trash/files/foo')
        self.logger.debug.assert_called_with('.trashinfo created as ~/.Trash/info/foo.trashinfo.')

    def test_should_create_a_trashinfo(self):

        self.trashdir.trash2('foo', self.now)

        self.fs.atomic_write.assert_called_with('~/.Trash/info/foo.trashinfo', ANY)
        self.logger.debug.assert_called_with('.trashinfo created as ~/.Trash/info/foo.trashinfo.')

    def test_trashinfo_should_contains_original_location_and_deletion_date(self):
        from datetime import datetime

        self.now.return_value = datetime(2012, 9, 25, 21, 47, 39)
        self.trashdir.trash2('foo', self.now)

        self.fs.atomic_write.assert_called_with(ANY,
                b'[Trash Info]\n'
                b'Path=foo\n'
                b'DeletionDate=2012-09-25T21:47:39\n')
        self.logger.debug.assert_called_with('.trashinfo created as ~/.Trash/info/foo.trashinfo.')

    def test_should_rollback_trashinfo_creation_on_problems(self):
        self.fs.move.side_effect = IOError

        try: self.trashdir.trash2('foo', self.now)
        except IOError: pass

        self.fs.remove_file.assert_called_with('~/.Trash/info/foo.trashinfo')
        self.logger.debug.assert_called_with('.trashinfo created as ~/.Trash/info/foo.trashinfo.')
