import unittest

from unit_tests.tools import assert_equal
from trashcli.put import TrashPutReporter


class TestTrashPutReporter(unittest.TestCase):
    def test_it_should_record_failures(self):

        reporter = TrashPutReporter(self)
        assert_equal(False, reporter.some_file_has_not_be_trashed)

        reporter.unable_to_trash_file('a file')
        assert_equal(True, reporter.some_file_has_not_be_trashed)
        assert_equal('cannot trash non existent \'a file\'', self.warning_msg)

    def warning(self, msg):
        self.warning_msg = msg

