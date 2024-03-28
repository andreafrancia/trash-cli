from abc import abstractmethod
from enum import Enum
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
    ('message', Message),
    ('tag', LogTag)
])):
    def resolve_message(self):
        return self.message.resolve()


class MessageStr(NamedTuple('Message', [
    ('message', str),
]), Message):
    def resolve(self):
        return self.message


def log_str(level,  # type: Level
            tag,  # type: LogTag
            message,  # type: str
            ):
    return LogEntry(level, MessageStr(message), tag)

def warning_str(message):  # type: (str) -> LogEntry
    return LogEntry(Level.WARNING, MessageStr(message), LogTag.unspecified)


def info_str(message):  # type: (str) -> LogEntry
    return LogEntry(Level.INFO, MessageStr(message), LogTag.unspecified)


def debug_str(message):  # type: (str) -> LogEntry
    return LogEntry(Level.DEBUG, MessageStr(message), LogTag.unspecified)
