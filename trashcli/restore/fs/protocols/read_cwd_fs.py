from trashcli.compat import Protocol


class ReadCwdFs(Protocol):
    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError()
