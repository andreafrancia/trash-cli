from abc import abstractmethod
from enum import Enum
from typing import List

from typing import NamedTuple

from trashcli.compat import Protocol


class Level(Enum):
    INFO = "INFO"
    DEBUG_FUNC = "DEBUG_FUNC"


class LogEntry(NamedTuple('LogEntry', [
    ('level', Level),
    ('message', str),
])):
    pass


class LogContext(NamedTuple('LogContext', [
    ('trashee_path', str),
    ('shrunk_candidate_path', str),
])):
    pass


class FailureReason(Protocol):
    @abstractmethod
    def log_entries(self, context):  # type: (LogContext) -> List[LogEntry]
        raise NotImplementedError
