from enum import Enum


def repr_for_enum(enum):  # type: (Enum) -> str
    return "%s.%s" % (type(enum).__name__, enum.name)
