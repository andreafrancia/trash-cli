from trashcli.compat import Protocol


class IntGenerator(Protocol):
    def new_int(self,
                 min,  # type: int
                 max,  # type: int
                 ):  # type: (...) -> int
        raise NotImplementedError
