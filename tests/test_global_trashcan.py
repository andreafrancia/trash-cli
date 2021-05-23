import unittest

from mock import Mock, call
from datetime import datetime

from trashcli.put import TrashResult, Trasher, TrashDirectoriesFinder, FileTrasher
import os

class TestTopDirRules:
    def test(self):
        parent_path = lambda _:None
        class MyVolumes:
            def volume_of(self, _path):
                return '/volume'
        volumes = MyVolumes()
        realpath = lambda _: None
        fs = Mock(['move',
                   'atomic_write',
                   'remove_file',
                   'ensure_dir',
                   'isdir',
                   'islink',
                   'has_sticky_bit'])
        fs.islink.side_effect = lambda path: {
                                                '/volume/.Trash':False
                                             }[path]
        fs.has_sticky_bit.side_effect = lambda path: {
                                                '/volume/.Trash':False
                                             }[path]
        reporter = Mock(['volume_of_file',
                         'found_unsecure_trash_dir_unsticky',
                         'trash_dir_with_volume',
                         'file_has_been_trashed_in_as',
                         'log_info'])
        trash_directories_finder = TrashDirectoriesFinder({},
                                                          lambda: 'uid',
                                                          volumes)
        file_trasher = FileTrasher(fs, volumes, realpath, datetime.now)
        trashcan = Trasher(trash_directories_finder,
                           file_trasher,
                           volumes,
                           parent_path)
        logger = Mock()
        result = TrashResult(False)
        trashcan.trash('', False, result, logger, False, reporter, None)
        assert [
            call('', '/volume/.Trash-uid')
            ] == reporter.file_has_been_trashed_in_as.mock_calls


class TestGlobalTrashCan(unittest.TestCase):
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()
        self.volumes = Mock()
        self.volumes.volume_of.return_value = '/'

        trash_directories_finder = TrashDirectoriesFinder(dict(),
                                                          lambda: 123,
                                                          self.volumes)
        file_trasher = FileTrasher(self.fs,
                                   self.volumes,
                                   lambda x: x,
                                   datetime.now)
        self.trasher = Trasher(trash_directories_finder,
                               file_trasher,
                               self.volumes,
                               os.path.dirname)
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

