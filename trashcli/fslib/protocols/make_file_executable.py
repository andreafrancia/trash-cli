from abc import abstractmethod

from trashcli.compat import Protocol


class MakeFileExecutable(Protocol):
    @abstractmethod
    def make_file_executable(self, path):
        raise NotImplementedError()
