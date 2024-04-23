from typing import IO

from typing import List

from tests.test_put.support.logs import Logs
from tests.test_put.support.log_line import LogLine
from trashcli.put.core.logs import LogData
from trashcli.put.core.logs import LogEntry
from trashcli.put.my_logger import LoggerBackend
from trashcli.put.my_logger import StreamBackend


class RecordingBackend(LoggerBackend):
    def __init__(self,
                 stderr,  # type: IO[str]
                 ):
        self.stderr = stderr
        self.logs = []  # type: List[LogLine]

    def write_message(self,
                      log_entry,  # type: LogEntry
                      log_data,  # type: LogData
                      ):
        StreamBackend(self.stderr).write_message(log_entry, log_data)
        self.logs.append(LogLine(log_entry.level,
                                 log_data.verbose,
                                 log_data.program_name,
                                 log_entry.resolve_message(),
                                 log_entry.tag))

    def collected(self):
        return Logs(self.logs)
