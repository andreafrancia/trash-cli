from typing import IO, Callable, List

from trashcli.put.core.logs import Level
from trashcli.put.core.logs import LogEntry


class LogData:
    def __init__(self, program_name, verbose):
        self.program_name = program_name
        self.verbose = verbose


class MyLogger:
    def __init__(self,
                 stderr,  # type: IO[str]
                 ):  # type: (...) -> None
        self.stderr = stderr

    def debug(self,
              message,  # type: str
              log_data,  # type: LogData
              ):  # type: (...) -> None
        if log_data.verbose > 1:
            self.stderr.write("%s: %s\n" % (log_data.program_name, message))

    def debug_func_result(self,
                          messages_func,  # type: Callable[[], List[str]]
                          log_data,  # type: LogData
                          ):
        if log_data.verbose > 1:
            for line in messages_func():
                self.stderr.write("%s: %s\n" % (log_data.program_name, line))

    def info(self,
             message,  # type: str
             log_data,  # type: LogData
             ):  # type: (...) -> None
        if log_data.verbose > 0:
            self.stderr.write("%s: %s\n" % (log_data.program_name, message))

    def warning2(self, message, program_name):
        self.stderr.write("%s: %s\n" % (program_name, message))

    def log_multiple(self, entries, log_data):  # type: (List[LogEntry], LogData) -> None
        for entry in entries:
            if entry.level == Level.INFO:
                self.info(entry.message, log_data)
            elif entry.level == Level.DEBUG:
                self.debug(entry.message, log_data)
            else:
                raise ValueError("unknown level: %s" % entry.level)
