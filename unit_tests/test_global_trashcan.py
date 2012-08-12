from mock import Mock
from nose.tools import istest

from trashcli.trash import GlobalTrashCan

class TestGlobalTrashCan:
    @istest
    def should_report_when_trash_fail(self):
        reporter = Mock()

        trashcan = GlobalTrashCan(environ = dict(),
                                  reporter = reporter,
                                  getuid = lambda:123,
                                  list_mount_points = None,
                                  now = None)

        trashcan.trash('non-existent')
        trashcan.reporter.unable_to_trash_file.assert_called_with('non-existent')
