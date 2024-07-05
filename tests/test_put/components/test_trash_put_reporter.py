from tests.support.mock import Mock
from six import StringIO
from trashcli.put.describer import Describer

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.put.my_logger import MyLogger
from trashcli.put.my_logger import StreamBackend
from trashcli.put.reporting.trash_put_reporter import TrashPutReporter


class TestTrashPutReporter:
    def setup_method(self):
        self.stderr = StringIO()
        self.backend = StreamBackend(self.stderr)
        self.fs = FakeFs()
        self.fs.touch("file")
        self.reporter = TrashPutReporter(self.fs)

    def test_it_should_record_failures(self):
        result = "\n".join(
            self.reporter.unable_to_trash_file_non_existent('file').
            resolve_messages())

        assert (result == "cannot trash regular empty file 'file'")
