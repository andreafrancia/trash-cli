from abc import abstractmethod
from typing import Callable, TypeVar, Generic

S = TypeVar("S")
R = TypeVar("R")
E = TypeVar("E")


class Either(Generic[S, E]):
    @abstractmethod
    def bind(self,
             func):  # type: (Callable[[S], Either[R, E]]) -> Either[R, E]
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):  # type: (object) -> bool
        raise NotImplementedError

    def is_error(self):  # type: () -> bool
        return not self.is_valid()

    def is_valid(self):  # type: () -> bool
        return {Left: False, Right: True}[type(self)]

    def error(self):  # type: () -> E
        if isinstance(self, Left):
            return self._error
        else:
            raise ValueError("Not an error: %s" % self)

    def value(self):
        if isinstance(self, Right):
            return self._value
        else:
            raise ValueError("Not a value: %s" % self)


class Right(Either[S, E]):
    def __init__(self, value):  # type: (S) -> None
        self._value = value

    def bind(self,
             func):  # type: (Callable[[S], Either[R, E]]) -> Either[R, E]
        return func(self._value)

    def __eq__(self, other):  # type: (object) -> bool
        return isinstance(other, Right) and self._value == other._value

    def __str__(self):  # type: () -> str
        return "Right %s" % self._value


class Left(Either[S, E]):
    def __init__(self, error):  # type: (E) -> None
        self._error = error

    def bind(self,
             func):  # type: (Callable[[S], Either[R, E]]) -> Either[R, E]
        return Left(self._error)

    def __eq__(self, other):  # type: (object) -> bool
        return isinstance(other, Left) and self._error == other._error

    def __str__(self):  # type: () -> str
        return "Left: %s" % self._error
