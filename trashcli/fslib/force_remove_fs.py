from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol


class ForceRemoveFs(Protocol):
    @abstractmethod
    def remove(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def shutil_rmtree(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def path_isdir(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def get_mod(self, path):  # type: (str) -> int
        raise NotImplementedError

    @abstractmethod
    def chmod(self, path, mode):  # type: (str, int) -> None
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError

    @abstractmethod
    def realpath(self, path):
        raise NotImplementedError
