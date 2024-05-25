from trashcli.compat import Protocol


class RestoreLogger(Protocol):
    def warning(self, message):
        raise NotImplementedError
