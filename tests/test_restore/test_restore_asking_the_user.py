import unittest

from mock import Mock, call
from trashcli.restore.restore_asking_the_user import RestoreAskingTheUser
from trashcli.restore.restorer import Restorer


class TestRestoreAskingTheUser(unittest.TestCase):
    def setUp(self):
        self.input = Mock(spec=[''])
        self.println = Mock(spec=[''])
        self.restorer = Mock(spec=Restorer)
        self.die = Mock(spec=[''])
        self.asking_user = RestoreAskingTheUser(self.input,
                                                self.println,
                                                self.restorer,
                                                self.die)

    def test(self):
        self.input.return_value = '0'

        self.asking_user.restore_asking_the_user(['trashed_file1',
                                                  'trashed_file2'])

        self.assertEqual([call('What file to restore [0..1]: ')],
                         self.input.mock_calls)
        self.assertEqual([], self.println.mock_calls)
        self.assertEqual([call.restore_trashed_file('trashed_file1', False)],
                         self.restorer.mock_calls)
        self.assertEqual([], self.die.mock_calls)

    def test2(self):
        self.input.side_effect = KeyboardInterrupt

        self.asking_user.restore_asking_the_user(['trashed_file1',
                                                  'trashed_file2'])

        self.assertEqual([call('What file to restore [0..1]: ')],
                         self.input.mock_calls)
        self.assertEqual([], self.println.mock_calls)
        self.assertEqual([], self.restorer.mock_calls)
        self.assertEqual([call('')], self.die.mock_calls)
