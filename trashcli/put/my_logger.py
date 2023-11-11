from typing import IO
from typing import List

from trashcli.put.core.logs import Level
from trashcli.put.core.logs import LogData
from trashcli.put.core.logs import LogEntry


class MyLogger:
    def __init__(self,
                 stderr,  # type: IO[str]
                 ):  # type: (...) -> None
        self.stderr = stderr

    def log_put(self,
                entry,  # type: LogEntry
                log_data,  # type: LogData
                ):
        min_level = {
            Level.WARNING: 0,
            Level.INFO: 1,
            Level.DEBUG: 2,
        }
        if log_data.verbose >= min_level[entry.level]:
            self.stderr.write("%s: %s\n" % (log_data.program_name,
                                            entry.resolve_message()))

    def log_multiple(self,
                     entries,  # type: List[LogEntry]
                     log_data,  # type: LogData
                     ):  # type: (...) -> None
        for entry in entries:
            self.log_put(entry, log_data)
