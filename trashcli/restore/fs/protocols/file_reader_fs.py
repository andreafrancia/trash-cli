from trashcli.compat import Protocol


class FileReaderFs(Protocol):
    def read_file(self,
                    path,  # type: str
                    ):  # type: (...) -> str
        raise NotImplementedError()
