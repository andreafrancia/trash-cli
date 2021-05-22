import unittest

from trashcli.put import TrashPutReporter


class TestTrashPutReporter(unittest.TestCase):
    def test_it_should_record_failures(self):
        reporter = TrashPutReporter(self, {})
        reporter.unable_to_trash_file('a file')
        assert 'cannot trash non existent \'a file\'' == self.warning_msg

    def warning(self, msg):
        self.warning_msg = msg

