from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol


class EmptyFs(Protocol):
    @abstractmethod
    def is_sticky_dir(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_world_writable(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def path_isdir(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def path_lexists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def remove(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def shutil_rmtree(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def read_file(self, path):  # type: (str) -> str
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
