from typing import NamedTuple


class FileToBeTrashed(NamedTuple('FileToBeTrashed', [
    ('path', str),
    ('volume', str)
])):
    pass
