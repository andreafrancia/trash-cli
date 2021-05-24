import unittest

from mock import Mock, call

from trashcli.put import Trasher


class TestTrasher(unittest.TestCase):
    def setUp(self):
        self.file_trasher = Mock(spec=['trash_file'])
        self.trasher = Trasher(self.file_trasher)

    def test(self):
        self.trasher.trash('file',
                           'user-trash-dir',
                           'result',
                           'logger',
                           False,
                           'reporter',
                           'forced_volume')

        assert self.file_trasher.mock_calls == \
               [call.trash_file(
                   'file',
                   'forced_volume',
                   'user-trash-dir',
                   'result',
                   'logger',
                   'reporter'
               )]
