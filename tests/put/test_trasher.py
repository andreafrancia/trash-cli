import unittest

from mock import Mock, call

from trashcli.put.trasher import Trasher
from trashcli.put.user import user_replied_no, user_replied_yes
from trashcli.put.trash_put_cmd import mode_force, mode_interactive


class TestTrasher(unittest.TestCase):
    def setUp(self):
        self.file_trasher = Mock(spec=['trash_file'])
        self.user = Mock()
        self.access = Mock(spec=['is_accessible'])
        self.access.is_accessible.return_value = True
        self.trasher = Trasher(self.file_trasher, self.user, self.access)
        self.file_trasher.trash_file.return_value = 'file_trasher result'

    def test(self):
        result = self.trasher.trash('file',
                                    'user-trash-dir',
                                    'result',
                                    'logger',
                                    mode_force,
                                    'reporter',
                                    'forced_volume',
                                    'program_name',
                                    {"env":"ironment"},
                                    123)

        assert [self.file_trasher.mock_calls,
                result] == \
               [
                   [call.trash_file(
                       'file',
                       'forced_volume',
                       'user-trash-dir',
                       'result',
                       'logger',
                       'reporter',
                       {"env": "ironment"},
                       123,
                   )],
                   'file_trasher result'
               ]

    def test_interactive_yes(self):
        self.user.ask_user_about_deleting_file.return_value = user_replied_yes

        result = self.trasher.trash('file',
                                    'user-trash-dir',
                                    'result',
                                    'logger',
                                    mode_interactive,
                                    'reporter',
                                    'forced_volume',
                                    'program_name',
                                    {"env":"ironment"},
                                    123)

        assert [self.user.mock_calls,
                self.file_trasher.mock_calls,
                result] == \
               [
                   [call.ask_user_about_deleting_file('program_name', 'file')],
                   [call.trash_file(
                       'file',
                       'forced_volume',
                       'user-trash-dir',
                       'result',
                       'logger',
                       'reporter',
                       {"env": "ironment"},
                       123,
                   )],
                   'file_trasher result'
               ]

    def test_interactive_no(self):
        self.user.ask_user_about_deleting_file.return_value = user_replied_no

        result = self.trasher.trash('file',
                                    'user-trash-dir',
                                    'result',
                                    'logger',
                                    mode_interactive,
                                    'reporter',
                                    'forced_volume',
                                    'program_name',
                                    {},
                                    123)

        assert [self.user.mock_calls,
                self.file_trasher.mock_calls,
                result] == \
               [
                   [call.ask_user_about_deleting_file('program_name', 'file')],
                   [],
                   'result'
               ]

    def test_dot_entry(self):
        self.reporter = Mock()
        self.trasher.trash('.',
                           'user-trash-dir',
                           'result',
                           'logger',
                           False,
                           self.reporter,
                           'forced_volume',
                           'program_name',
                           {},
                                    123)

        assert self.reporter.mock_calls == \
               [call.unable_to_trash_dot_entries('.')]
