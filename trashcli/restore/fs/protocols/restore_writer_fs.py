from trashcli.compat import Protocol


class RestoreWriterFs(Protocol):
    def mkdirs(self, path):  # type: (str) -> None
        raise NotImplementedError()

    def move(self, src, dst):  # type: (str, str) -> None
        raise NotImplementedError()

    def remove_file(self, path):  # type: (str) -> None
        raise NotImplementedError()
