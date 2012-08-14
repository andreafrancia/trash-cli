from mock import Mock
from nose.tools import istest

from trashcli.trash import GlobalTrashCan

class TestGlobalTrashCan:
    def setUp(self):
        self.reporter = Mock()

        self.trashcan = GlobalTrashCan(environ = dict(),
                                  reporter = self.reporter,
                                  getuid = lambda:123,
                                  list_mount_points = None,
                                  now = None)

    @istest
    def should_report_when_trash_fail(self):

        self.trashcan.trash('non-existent')
        self.reporter.unable_to_trash_file.assert_called_with('non-existent')


