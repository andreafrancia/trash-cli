from typing import IO
from typing import List

from trashcli.compat import Protocol
from trashcli.put.core.logs import Level
from trashcli.put.core.logs import LogData
from trashcli.put.core.logs import LogEntry


class LoggerBackend(Protocol):
    def write_message(self,
                      log_entry,  # type: LogEntry
                      log_data,  # type: LogData
                      ):
        raise NotImplementedError()


class StreamBackend(LoggerBackend):
    def __init__(self,
                 stderr,  # type: IO[str]
                 ):  # type: (...) -> None
        self.stderr = stderr

    def write_message(self,
                      log_entry,  # type: LogEntry
                      log_data,  # type: LogData
                      ):
        if is_right_for_level(log_data.verbose, log_entry.level):
            self.stderr.write("%s: %s\n" % (log_data.program_name,
                                            log_entry.resolve_message()))


def is_right_for_level(verbose,  # type: int
                       level,  # type: Level
                       ):
    min_level = {
        Level.WARNING: 0,
        Level.INFO: 1,
        Level.DEBUG: 2,
    }
    return verbose >= min_level[level]


class MyLogger:
    def __init__(self,
                 backend,  # type: LoggerBackend
                 ):  # type: (...) -> None
        self.backend = backend

    def log_put(self,
                entry,  # type: LogEntry
                log_data,  # type: LogData
                ):
        self.backend.write_message(entry, log_data)

    def log_multiple(self,
                     entries,  # type: List[LogEntry]
                     log_data,  # type: LogData
                     ):  # type: (...) -> None
        for entry in entries:
            self.log_put(entry, log_data)
