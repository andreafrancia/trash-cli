from typing import Generic, Iterator, TypeVar, Type

from trashcli.put.core.logs import LogEntry, Level
from trashcli.put.my_logger import MyLogger, LogData

R = TypeVar('R')


class JobStatus(Generic[R]):
    def __init__(self, message):  # type: (str) -> None
        self.log_entries = [LogEntry(Level.DEBUG, message)]

    def has_succeeded(self):
        return isinstance(self, Succeeded)

    def result(self):  # type: () -> R
        raise NotImplementedError

    def logs(self):
        return self.log_entries


class NeedsMoreAttempts(JobStatus, Generic[R]):
    def __init__(self,
                 trashinfo_path,  # type: str
                 message,  # type: str
                 ):
        super(NeedsMoreAttempts, self).__init__(message)
        self.trashinfo_path = trashinfo_path

    def result(self):  # type: () -> R
        raise ValueError("Result not available yet!")


class Succeeded(JobStatus, Generic[R]):
    def __init__(self,
                 result,  # type: R
                 message,  # type: str
                 ):
        super(Succeeded, self).__init__(message)
        self._result = result  # type: R

    def result(self):  # type: () -> R
        return self._result

    def __repr__(self):
        return "Succeeded(%s)" % repr(self.result)


class JobExecutor(Generic[R]):
    def __init__(self,
                 logger,  # type: MyLogger
                 _result_type,  # type: Type[R]
                 ):
        self.logger = logger

    def execute(self,
                job,  # type: Iterator[JobStatus[R]]
                log_data,  # type: LogData
                ):  # type: (...) -> R
        for status in job:
            self.logger.log_multiple(status.logs(), log_data)
            if status.has_succeeded():
                return status.result()
        raise ValueError("Should not happen!")
