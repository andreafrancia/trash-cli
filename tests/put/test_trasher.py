import unittest

from mock import Mock, call

from trashcli.put import Trasher


class TestTrasher(unittest.TestCase):
    def setUp(self):
        self.trash_directories_finder = Mock(spec=['possible_trash_directories_for'])
        self.trash_directories_finder.possible_trash_directories_for.return_value = ['dir1', 'dir2']
        self.file_trasher = Mock(spec=['try_trash_file_using_candidates'])
        self.volumes = Mock(spec=['volume_of'])
        self.volumes.volume_of.side_effect = lambda x: 'volume_of %s' % x
        self.parent_path = lambda x: 'parent path of %s' % x
        self.reporter = Mock(spec=['volume_of_file'])
        self.trasher = Trasher(self.trash_directories_finder,
                               self.file_trasher,
                               self.volumes,
                               self.parent_path)

    def test(self):
        self.trasher.trash('file',
                           'user-trash-dir',
                           'result',
                           'logger',
                           False,
                           self.reporter,
                           None)

        assert self.trash_directories_finder.mock_calls == \
               [call.possible_trash_directories_for(
                   'volume_of parent path of file', 'user-trash-dir')]
        assert self.file_trasher.mock_calls == \
               [call.try_trash_file_using_candidates(
                   'file',
                   'volume_of parent path of file',
                   ['dir1', 'dir2'],
                   'result',
                   'logger',
                   self.reporter
               )]
