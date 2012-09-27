from unittest import TestCase

from mock import Mock
from nose.tools import istest, assert_true, assert_equals

from trashcli.put import GlobalTrashCan


class TestGlobalTrashCan:
    def setUp(self):
        self.reporter = Mock()

        self.trashcan = GlobalTrashCan(
                home_trashcan = Mock(),
                reporter = self.reporter,
                getuid = lambda:123,
                now = None)

    @istest
    def should_report_when_trash_fail(self):

        self.trashcan.trash('non-existent')
        self.reporter.unable_to_trash_file.assert_called_with('non-existent')

class TestGlobalTrashCan2(TestCase):
    def test_the_attempt_of_deleting_a_dot_directory_should_signaled_as_error(self):

        argument="."

        class StubReporter:
            def __init__(self):
                self.has_been_called=False

            def unable_to_trash_dot_entries(self,file):
                self.has_been_called=True
                assert_equals(file, argument)

        reporter=StubReporter()
        trashcan = GlobalTrashCan(
                reporter=reporter,
                home_trashcan = Mock(),
                )

        trashcan.trash('.')
        assert_true(reporter.has_been_called)
