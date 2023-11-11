from abc import abstractmethod
from enum import Enum
from typing import NamedTuple
from typing import Protocol


class Level(Enum):
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARNING = "WARNING"


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
])):
    def resolve_message(self):
        return self.message.resolve()


class MessageStr(NamedTuple('Message', [
    ('message', str),
]), Message):
    def resolve(self):
        return self.message


def warning_str(message):  # type: (str) -> LogEntry
    return LogEntry(Level.WARNING, MessageStr(message))


def info_str(message):  # type: (str) -> LogEntry
    return LogEntry(Level.INFO, MessageStr(message))


def debug_str(message):  # type: (str) -> LogEntry
    return LogEntry(Level.DEBUG, MessageStr(message))
