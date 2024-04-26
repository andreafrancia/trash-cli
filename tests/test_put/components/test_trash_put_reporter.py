from mock import Mock
from six import StringIO

from trashcli.put.my_logger import MyLogger
from trashcli.put.my_logger import StreamBackend
from trashcli.put.reporting.trash_put_reporter import TrashPutReporter


class TestTrashPutReporter:
    def setup_method(self):
        self.stderr = StringIO()
        self.backend = StreamBackend(self.stderr)
        describer = Mock()
        describer.describe.return_value = "file-description"
        self.reporter = TrashPutReporter(describer)

    def test_it_should_record_failures(self):
        result = "\n".join(
            self.reporter.unable_to_trash_file_non_existent('a file').
            resolve_messages())

        assert (result == "cannot trash file-description 'a file'")
