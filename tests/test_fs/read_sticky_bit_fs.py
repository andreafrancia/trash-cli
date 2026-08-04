from trashcli.compat import Protocol


class ReadStickyBitFs(Protocol):
    def is_sticky(self,
                  path,  # type: str
                  ):  # type: (...) -> bool
        raise NotImplementedError
