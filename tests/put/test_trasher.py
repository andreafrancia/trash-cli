import unittest

from mock import Mock, call

from trashcli.put import Trasher


class TestTrasher(unittest.TestCase):
    def setUp(self):
        self.file_trasher = Mock(spec=['try_trash_file_using_candidates'])
        self.volumes = Mock(spec=['volume_of'])
        self.volumes.volume_of.side_effect = lambda x: 'volume_of %s' % x
        self.parent_path = lambda x: 'parent path of %s' % x
        self.reporter = Mock(spec=['volume_of_file'])
        self.trasher = Trasher(self.file_trasher)

    def test(self):
        self.trasher.trash('file',
                           'user-trash-dir',
                           'result',
                           'logger',
                           False,
                           self.reporter,
                           'forced_volume')

        assert self.file_trasher.mock_calls == \
               [call.try_trash_file_using_candidates(
                   'file',
                   'forced_volume',
                   'user-trash-dir',
                   'result',
                   'logger',
                   self.reporter
               )]
