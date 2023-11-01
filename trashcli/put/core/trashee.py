from typing import NamedTuple


class Trashee(NamedTuple('FileToBeTrashed', [
    ('path', str),
    ('volume', str)
])):
    pass
