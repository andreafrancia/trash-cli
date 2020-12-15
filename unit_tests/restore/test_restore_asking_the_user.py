import unittest

from mock import Mock, call

from trashcli.restore import RestoreAskingTheUser


class TestRestoreAskingTheUser(unittest.TestCase):
    def setUp(self):
        self.input = Mock(spec=[''])
        self.println = Mock(spec=[''])
        self.restore = Mock(spec=[''])
        self.die = Mock(spec=[''])
        self.restorer = RestoreAskingTheUser(self.input,
                                             self.println,
                                             self.restore,
                                             self.die)

    def test(self):
        self.input.return_value = '0'

        self.restorer.restore_asking_the_user(['trashed_file1',
                                               'trashed_file2'])

        self.assertEqual([call('What file to restore [0..1]: ')],
                         self.input.mock_calls)
        self.assertEqual([], self.println.mock_calls)
        self.assertEqual([call('trashed_file1')] ,
                         self.restore.mock_calls)
        self.assertEqual([], self.die.mock_calls)
