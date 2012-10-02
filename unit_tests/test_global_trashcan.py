from unittest import TestCase

from mock import Mock
from nose.tools import istest, assert_true, assert_equals

from trashcli.put import GlobalTrashCan

class TestGlobalTrashCan:
    def setUp(self):
        self.reporter = Mock()
        self.fs = Mock()

        self.trashcan = GlobalTrashCan(
                reporter = self.reporter,
                getuid = lambda:123,
                now = None,
                environ = dict(),
                fs = self.fs)

    @istest
    def should_report_when_trash_fail(self):
        self.fs.move.side_effect = IOError

        self.trashcan.trash('non-existent')

        self.reporter.unable_to_trash_file.assert_called_with('non-existent')

    @istest
    def should_not_delete_a_dot_entru(self):

        self.trashcan.trash('.')

        self.reporter.unable_to_trash_dot_entries.assert_called_with('.')

