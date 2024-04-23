from typing import NamedTuple

from trashcli.put.core.logs import Level
from trashcli.put.core.logs import LogTag


class LogLine(NamedTuple('LogLine', [
    ('level', Level),
    ('verbose', int),
    ('program_name', str),
    ('message', str),
    ('tag', LogTag)
])):
    pass
