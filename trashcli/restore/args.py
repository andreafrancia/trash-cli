from six import add_metaclass
from typing import NamedTuple, Optional, Union
from typing import Type

from trashcli.put.class_name_meta import ClassNameMeta


class Sort:
    @add_metaclass(ClassNameMeta)
    class ByDate: pass

    @add_metaclass(ClassNameMeta)
    class ByPath: pass

    @add_metaclass(ClassNameMeta)
    class DoNot: pass

    Type = Union[Type[ByDate], Type[ByPath], Type[DoNot]]


class RunRestoreArgs(
    NamedTuple('RunRestoreArgs', [
        ('path', str),
        ('sort', Sort.Type),
        ('trash_dir', Optional[str]),
        ('overwrite', bool),
    ])):
    pass
