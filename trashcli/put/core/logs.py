from enum import Enum
from typing import NamedTuple


class Level(Enum):
    INFO = "INFO"
    DEBUG_FUNC = "DEBUG_FUNC"
    DEBUG = "DEBUG"


class LogEntry(NamedTuple('LogEntry', [
    ('level', Level),
    ('message', str),
])):
    pass
