import unittest

from mock import Mock
from datetime import datetime

from trashcli.put import TrashResult, Trasher, FileTrasher
import os


class TestGlobalTrashCan(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()
        self.volumes = Mock()
        self.volumes.volume_of.return_value = '/'

        trash_directories_finder = Mock(spec=['possible_trash_directories_for'])
        trash_directories_finder.possible_trash_directories_for.return_value = []
        file_trasher = FileTrasher(self.fs,
                                   self.volumes,
                                   lambda x: x,
                                   datetime.now,
                                   trash_directories_finder,
                                   os.path.dirname)
        self.trasher = Trasher(file_trasher)
        self.logger = Mock()
        self.ignore_missing = False

    def test_log_volume(self):
        result = TrashResult(False)
        self.trasher.trash('a-dir/with-a-file',
                           False,
                           result,
                           self.logger,
                           self.ignore_missing,
                           self.reporter,
                           None)

        self.reporter.volume_of_file.assert_called_with('/')

    def test_should_report_when_trash_fail(self):
        self.fs.move.side_effect = IOError

        result = TrashResult(False)
        self.trasher.trash('non-existent',
                           False,
                           result,
                           self.logger,
                           self.ignore_missing,
                           self.reporter,
                           None)

        self.reporter.unable_to_trash_file.assert_called_with('non-existent')

    def test_should_not_delete_a_dot_entru(self):

        result = TrashResult(False)
        self.trasher.trash('.',
                           False,
                           result,
                           self.logger,
                           self.ignore_missing,
                           self.reporter,
                           None)

        self.reporter.unable_to_trash_dot_entries.assert_called_with('.')

    def test_bug(self):
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
        self.volumes.volume_of.side_effect = (lambda path: {
            '/foo': '/',
            '': '/',
            '/.Trash/123': '/',
            }[path])

        result = TrashResult(False)
        self.trasher.trash('foo',
                           False,
                           result,
                           self.logger,
                           self.ignore_missing,
                           self.reporter,
                           None)

