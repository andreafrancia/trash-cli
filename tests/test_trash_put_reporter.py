import unittest

from mock import Mock, call

from trashcli.put.reporter import TrashPutReporter


class TestTrashPutReporter(unittest.TestCase):
    def test_it_should_record_failures(self):
        logger = Mock(['warning2'])
        reporter = TrashPutReporter(logger, {})
        reporter.unable_to_trash_file('a file', 'trash-put')
        assert [call('cannot trash non existent \'a file\'', 'trash-put')] == \
               logger.warning2.mock_calls
