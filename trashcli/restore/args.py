from enum import Enum
from typing import NamedTuple, Optional

from trashcli.lib.enum_repr import repr_for_enum


class Sort(Enum):
    ByDate = "ByDate"
    ByPath = "ByPath"
    DoNot = "DoNot"

    def __repr__(self):
        return repr_for_enum(self)


class RunRestoreArgs(
    NamedTuple('RunRestoreArgs', [
        ('path', str),
        ('sort', Sort),
        ('trash_dir', Optional[str]),
        ('overwrite', bool),
    ])):
    pass
