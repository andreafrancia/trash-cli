from trashcli.compat import Protocol


class FileReaderFs(Protocol):
    def contents_of(self, path):
        raise NotImplementedError()
