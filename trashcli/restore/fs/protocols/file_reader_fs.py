from abc import abstractmethod

from trashcli.compat import Protocol


class FileReaderFs(Protocol):
    @abstractmethod
    def read_file(self,
                    path,  # type: str
                    ):  # type: (...) -> str
        raise NotImplementedError()
