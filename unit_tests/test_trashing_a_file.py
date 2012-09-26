from trashcli.trash import TrashDirectory
from mock import Mock
from nose.tools import istest
from mock import ANY

class TestTrashing:
    def setUp(self):
        self.move = Mock()
        self.atomic_write = Mock()
        self.now = Mock()
        self.remove_file = Mock()
        self.ensure_dir = Mock()
        self.trashdir = TrashDirectory('~/.Trash', '/',
                move         = self.move,
                atomic_write = self.atomic_write,
                now          = self.now,
                remove_file  = self.remove_file,
                ensure_dir   = self.ensure_dir)
        self.trashdir.store_relative_paths()
        path_for_trash_info = Mock()
        path_for_trash_info.for_file.return_value = 'foo'
        self.trashdir.path_for_trash_info = path_for_trash_info

    @istest
    def the_file_should_be_moved_in_trash_dir(self):

        self.trashdir.trash('foo')

        self.move.assert_called_with('foo', '~/.Trash/files/foo')

    @istest
    def test_should_create_a_trashinfo(self):

        self.trashdir.trash('foo')

        self.atomic_write.assert_called_with('~/.Trash/info/foo.trashinfo', ANY)

    @istest
    def trashinfo_should_contains_original_location_and_deletion_date(self):
        from datetime import datetime

        self.now.return_value = datetime(2012, 9, 25, 21, 47, 39)
        self.trashdir.trash('foo')

        self.atomic_write.assert_called_with(ANY,
                '[Trash Info]\n'
                'Path=foo\n'
                'DeletionDate=2012-09-25T21:47:39\n')

    @istest
    def should_rollback_trashinfo_creation_on_problems(self):
        self.move.side_effect = IOError

        try: self.trashdir.trash('foo')
        except IOError: pass

        self.remove_file.assert_called_with('~/.Trash/info/foo.trashinfo')
