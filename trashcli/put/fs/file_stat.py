from typing import NamedTuple


class Stat(NamedTuple('Stat', [
    ('mode', int),
    ('uid', int),
    ('gid', int),
])):
    pass
