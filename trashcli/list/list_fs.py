from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol


class ListFs(Protocol):
    @abstractmethod
    def is_sticky_dir(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def has_sticky_bit(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def read_file(self, path):
        raise NotImplementedError

    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_world_writable(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
