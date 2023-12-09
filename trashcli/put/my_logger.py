from typing import IO
from typing import List

from trashcli.compat import Protocol
from trashcli.put.core.logs import Level
from trashcli.put.core.logs import LogData
from trashcli.put.core.logs import LogEntry


class LoggerBackend(Protocol):
    def write_message(self,
                      level,  # type: Level
                      verbose,  # type: int
                      program_name,  # type: str
                      message,  # type: str
                      ):
        raise NotImplementedError()


class RecordingBackend(LoggerBackend):
    def __init__(self,
                 stderr,  # type: IO[str]
                 ):
        self.stderr = stderr
        self.logs = []

    def write_message(self,
                      level,  # type: Level
                      verbose,  # type: int
                      program_name,  # type: str
                      message,  # type: str
                      ):
        StreamBackend(self.stderr).write_message(level, verbose,
                                                 program_name, message)
        self.logs.append((message,))


class StreamBackend(LoggerBackend):
    def __init__(self,
                 stderr,  # type: IO[str]
                 ):  # type: (...) -> None
        self.stderr = stderr

    def write_message(self,
                      level,  # type: Level
                      verbose,  # type: int
                      program_name,  # type: str
                      message,  # type: str
                      ):
        if is_right_for_level(verbose, level):
            self.stderr.write("%s: %s\n" % (program_name, message))


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
        self.backend.write_message(
            entry.level,
            log_data.verbose,
            log_data.program_name,
            entry.resolve_message(),
        )

    def log_multiple(self,
                     entries,  # type: List[LogEntry]
                     log_data,  # type: LogData
                     ):  # type: (...) -> None
        for entry in entries:
            self.log_put(entry, log_data)
