import unittest

from trashcli.put import TrashPutReporter


class TestTrashPutReporter(unittest.TestCase):
    def test_it_should_record_failures(self):

        reporter = TrashPutReporter(self, {})
        assert False == reporter.some_file_has_not_be_trashed

        reporter.unable_to_trash_file('a file')
        assert True == reporter.some_file_has_not_be_trashed
        assert 'cannot trash non existent \'a file\'' == self.warning_msg

    def warning(self, msg):
        self.warning_msg = msg

