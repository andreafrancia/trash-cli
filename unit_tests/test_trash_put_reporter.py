from nose.tools import assert_equals
from nose.tools import istest
from trashcli.trash import TrashPutReporter

class TestTrashPutReporter:
    @istest
    def it_should_record_failures(self):

        reporter = TrashPutReporter()
        assert_equals(True, reporter.all_files_have_been_trashed)

        reporter.unable_to_trash_file('a file')
        assert_equals(False, reporter.all_files_have_been_trashed)

