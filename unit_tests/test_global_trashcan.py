from mock import Mock
from nose.tools import istest

from trashcli.put import GlobalTrashCan
import os

class TestGlobalTrashCan:
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()
        self.volume_of = Mock()
        self.volume_of.return_value = '/'

        self.trashcan = GlobalTrashCan(
                volume_of = self.volume_of,
                reporter = self.reporter,
                getuid = lambda:123,
                now = None,
                environ = dict(),
                fs = self.fs,
                parent_path = os.path.dirname)

    def test_log_volume(self):
        self.trashcan.trash('a-dir/with-a-file')

        self.reporter.volume_of_file.assert_called_with('/')

    @istest
    def should_report_when_trash_fail(self):
        self.fs.move.side_effect = IOError

        self.trashcan.trash('non-existent')

        self.reporter.unable_to_trash_file.assert_called_with('non-existent')

    @istest
    def should_not_delete_a_dot_entru(self):

        self.trashcan.trash('.')

        self.reporter.unable_to_trash_dot_entries.assert_called_with('.')

    @istest
    def bug(self):
        self.fs.mock_add_spec([
            'move',
            'atomic_write',
            'remove_file',
            'ensure_dir',

            'isdir',
            'islink',
            'has_sticky_bit',
            ], True)
        self.fs.islink.side_effect = (lambda path: { '/.Trash':False }[path])
        self.volume_of.side_effect = (lambda path: {
            '/foo': '/',
            '': '/',
            '/.Trash/123': '/',
            }[path])

        self.trashcan.trash('foo')

    def test_what_happen_when_trashing_with_trash_dir(self):
        from trashcli.put import TrashDirectoryForPut
        fs = Mock()
        now = Mock()
        fs.mock_add_spec([
            'move', 'atomic_write', 'remove_file', 'ensure_dir',
            ], True)

        from nose import SkipTest
        raise SkipTest()

        trash_dir = TrashDirectoryForPut('/path', '/volume', now, fs)

        trash_dir.trash('garbage')

