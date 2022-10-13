import unittest

from typing import cast

import flexmock
from mock import Mock, call
from trashcli.put.parser import mode_force, mode_interactive
from trashcli.put.real_fs import RealFs
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_result import TrashResult
from trashcli.put.trasher import Trasher
from trashcli.put.user import user_replied_no, user_replied_yes


class TestTrasher(unittest.TestCase):
    def setUp(self):
        self.file_trasher = Mock(spec=['trash_file'])
        self.user = Mock()
        self.access = Mock(spec=['is_accessible'])
        self.access.is_accessible.return_value = True
        self.reporter = Mock(spec=['unable_to_trash_dot_entries'])
        self.fs = flexmock.Mock(spec=RealFs)
        self.trasher = Trasher(self.file_trasher, self.user, self.access,
                               cast(TrashPutReporter, self.reporter),
                               cast(RealFs, self.fs))
        self.file_trasher.trash_file.return_value = 'file_trasher result'

    def test(self):
        result = self.trasher.trash('file',
                                    'user-trash-dir',
                                    cast(TrashResult, 'result'),
                                    mode_force,
                                    'forced_volume',
                                    'program_name',
                                    99,
                                    {"env": "ironment"},
                                    123)

        assert [self.file_trasher.mock_calls,
                result] == \
               [
                   [call.trash_file(
                       'file',
                       'forced_volume',
                       'user-trash-dir',
                       'result',
                       {"env": "ironment"},
                       123,
                       'program_name',
                       99,
                   )],
                   'file_trasher result'
               ]

    def test_interactive_yes(self):
        self.user.ask_user_about_deleting_file.return_value = user_replied_yes

        result = self.trasher.trash('file',
                                    'user-trash-dir',
                                    'result',
                                    mode_interactive,
                                    'forced_volume',
                                    'program_name',
                                    99,
                                    {"env": "ironment"},
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
                       {"env": "ironment"},
                       123,
                       'program_name',
                       99,
                   )],
                   'file_trasher result'
               ]

    def test_interactive_no(self):
        self.user.ask_user_about_deleting_file.return_value = user_replied_no

        result = self.trasher.trash('file',
                                    'user-trash-dir',
                                    'result',
                                    mode_interactive,
                                    'forced_volume',
                                    'program_name',
                                    {},
                                    123,
                                    99)

        assert [self.user.mock_calls,
                self.file_trasher.mock_calls,
                result] == \
               [
                   [call.ask_user_about_deleting_file('program_name', 'file')],
                   [],
                   'result'
               ]

    def test_dot_entry(self):
        self.trasher.trash('.',
                           'user-trash-dir',
                           'result',
                           False,
                           'forced_volume',
                           'program_name',
                           {},
                           123,
                           99)

        assert self.reporter.mock_calls == \
               [call.unable_to_trash_dot_entries('.', 'program_name')]
