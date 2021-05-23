import unittest

from mock import Mock, call

from trashcli.put import TrashPutReporter


class TestTrashPutReporter(unittest.TestCase):
    def test_it_should_record_failures(self):
        logger = Mock(['warning2'])
        reporter = TrashPutReporter(logger, {})
        reporter.unable_to_trash_file('a file')
        assert [call('cannot trash non existent \'a file\'')] == \
               logger.warning2.mock_calls
