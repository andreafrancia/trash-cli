import unittest

from mock import Mock, call

from trashcli.put import Trasher, mode_interactive, mode_force


class TestTrasher(unittest.TestCase):
    def setUp(self):
        self.file_trasher = Mock(spec=['trash_file'])
        self.user = Mock()
        self.access = Mock(spec=['is_accessible'])
        self.access.is_accessible.return_value = True
        self.trasher = Trasher(self.file_trasher, self.user, self.access)

    def test(self):
        self.trasher.trash('file',
                           'user-trash-dir',
                           'result',
                           'logger',
                           mode_force,
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

    def test_interactive(self):
        self.trasher.trash('file',
                           'user-trash-dir',
                           'result',
                           'logger',
                           mode_interactive,
                           'reporter',
                           'forced_volume',
                           'program_name')

        assert [self.user.mock_calls,
                self.file_trasher.mock_calls] == \
               [
                   [call.ask_user_about_deleting_file('program_name', 'file')],
                   [call.trash_file(
                       'file',
                       'forced_volume',
                       'user-trash-dir',
                       'result',
                       'logger',
                       'reporter'
                   )]
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
                           'program_name')

        assert self.reporter.mock_calls == \
               [call.unable_to_trash_dot_entries('.')]
