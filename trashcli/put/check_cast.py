from typing import Any
from typing import Type
from typing import TypeVar
from typing import cast

T = TypeVar('T')


def check_cast(t, value):  # type: (Type[T], Any) -> T
    if isinstance(value, t):
        return cast(t, value)  # type: ignore
    else:
        raise TypeError("expected %s, got %s" % (t, type(value)))
