import os
from typing import NamedTuple


class Trashee(NamedTuple('FileToBeTrashed', [
    ('path', str),
    ('volume', str)
])):
    pass


def should_skipped_by_specs(path):
    basename = os.path.basename(path)
    return (basename == ".") or (basename == "..")
