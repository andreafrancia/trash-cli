from nose.tools import assert_equals
from nose.tools import istest
from trashcli.put import TrashPutReporter

class TestTrashPutReporter:
    @istest
    def it_should_record_failures(self):

        reporter = TrashPutReporter(self)
        assert_equals(False, reporter.some_file_has_not_be_trashed)

        reporter.unable_to_trash_file('a file')
        assert_equals(True, reporter.some_file_has_not_be_trashed)
        assert_equals('cannot trash non existent \'a file\'', self.warning_msg)

    def warning(self, msg):
        self.warning_msg = msg

