import unittest

from mock import Mock, call

from trashcli.put import Trasher


class TestTrasher(unittest.TestCase):
    def setUp(self):
        self.file_trasher = Mock(spec=['trash_file'])
        self.input = Mock()
        self.trasher = Trasher(self.file_trasher, self.input)

    def test(self):
        self.trasher.trash('file',
                           'user-trash-dir',
                           'result',
                           'logger',
                           False,
                           'reporter',
                           'forced_volume',
                           'program_name')

        assert self.file_trasher.mock_calls == \
               [call.trash_file(
                   'file',
                   'forced_volume',
                   'user-trash-dir',
                   'result',
                   'logger',
                   'reporter'
               )]

    def test_dot_entry(self):
        self.reporter = Mock()
        self.trasher.trash('.',
                           'user-trash-dir',
                           'result',
                           'logger',
                           False,
                           self.reporter,
                           'forced_volume',
                           'program_name')

        assert self.reporter.mock_calls == \
               [call.unable_to_trash_dot_entries('.')]
