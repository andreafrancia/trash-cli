import unittest

from mock import Mock
from six import StringIO

from trashcli.put.my_logger import LogData
from trashcli.put.my_logger import MyLogger
from trashcli.put.my_logger import StreamBackend
from trashcli.put.reporter import TrashPutReporter


class TestTrashPutReporter(unittest.TestCase):
    def setUp(self):
        self.stderr = StringIO()
        self.backend = StreamBackend(self.stderr)
        self.logger = MyLogger(self.backend)
        describer = Mock()
        describer.describe.return_value = "file-description"
        self.reporter = TrashPutReporter(self.logger, describer)

    def test_it_should_record_failures(self):
        self.reporter.unable_to_trash_file_non_existent('a file', LogData('trash-put', 99))

        assert (self.stderr.getvalue() ==
                "trash-put: cannot trash file-description 'a file'\n")
