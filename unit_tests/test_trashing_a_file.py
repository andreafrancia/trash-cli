from trashcli.trash import TrashDirectory
from mock import Mock
from nose.tools import assert_equals

class TestTrashing:
    def test(self):
        self.move = Mock()
        self.trashdir = TrashDirectory('~/.Trash', '/', self.move)
        self.trashdir.store_relative_paths()
        self.trashdir.persist_trash_info = Mock(
                return_value='~/.Trash/info/foo.trashinfo')

        self.trashdir.trash('foo')

        self.move.assert_called_with('foo', '~/.Trash/files/foo')


