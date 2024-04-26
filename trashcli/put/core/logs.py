from abc import abstractmethod
from enum import Enum
from typing import List
from typing import NamedTuple
from trashcli.compat import Protocol


class Level(Enum):
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARNING = "WARNING"


class LogTag(Enum):
    "tags used only during testing"
    unspecified = "unspecified"
    trash_failed = "trash_failed"


class LogData:
    def __init__(self, program_name, verbose):
        self.program_name = program_name
        self.verbose = verbose


class Message(Protocol):
    @abstractmethod
    def resolve(self):
        raise NotImplementedError


class LogEntry(NamedTuple('LogEntry', [
    ('level', Level),
    ('tag', LogTag),
    ('messages', List[Message]),
])):
    def resolve_messages(self):
        for m in self.messages:
            yield m.resolve()


class MessageStr(NamedTuple('Message', [
    ('message', str),
]), Message):
    def resolve(self):
        return self.message

    @staticmethod
    def from_messages(messages  # type: List[str]
                      ):
        return [MessageStr(msg) for msg in messages]


def log_str(level,  # type: Level
            tag,  # type: LogTag
            message,  # type: str
            ):
    return LogEntry(level, tag, MessageStr.from_messages([message]))


def warning_str(message):  # type: (str) -> LogEntry
    return log_str(Level.WARNING, LogTag.unspecified, message)


def info_str(message):  # type: (str) -> LogEntry
    return log_str(Level.INFO, LogTag.unspecified, message)


def debug_str(message):  # type: (str) -> LogEntry
    return log_str(Level.DEBUG, LogTag.unspecified, message)
