from abc import abstractmethod
from typing import Iterable
from trashcli.compat import Protocol


class RmFs(Protocol):
    @abstractmethod
    def read_file(self, path):
        raise NotImplementedError()

    @abstractmethod
    def entries_if_dir_exists(self, path):  # type: (str) -> Iterable[str]
        raise NotImplementedError()

    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()

    @abstractmethod
    def path_isdir(self, path):  # type: (str) -> bool
        raise NotImplementedError()

    @abstractmethod
    def is_sticky_dir(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def remove_file2(self, path):
        raise NotImplementedError()

    @abstractmethod
    def remove_file_if_exists(self, path):
        raise NotImplementedError()
