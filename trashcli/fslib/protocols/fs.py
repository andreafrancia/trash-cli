import os
from abc import abstractmethod
from typing import List, Optional, Tuple, Iterable

from trashcli.compat import Protocol


class Fs(Protocol):
    # notes:
    #  - the use of @abstractmethod the use of abstract method ensure that
    #    implementation of this protocol cannot be instantiated if not all the
    #    methods are implemented.
    #  - Fs it a big protocol and it is expected to be implemented only by two
    #    classes: FakeFs and RealFs.

    @abstractmethod
    def mkdirs(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def realpath(self, path):  # type: (str) -> str
        raise NotImplementedError

    @abstractmethod
    def touch(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def volume_of(self, path):  # type: (str) -> str
        raise NotImplementedError

    @abstractmethod
    def symlink(self, src, dest):  # type: (str, str) -> None
        raise NotImplementedError

    @abstractmethod
    def mkdir(self, path, mode=0o777):  # type: (str, int) -> None
        raise NotImplementedError

    @abstractmethod
    def atomic_write(self, path, content):  # type: (str, str) -> None
        raise NotImplementedError

    @abstractmethod
    def chmod(self, path, mode):  # type: (str, int) -> None
        raise NotImplementedError

    @abstractmethod
    def path_isdir(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def isfile(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def file_size(self, path):  # type: (str) -> int
        raise NotImplementedError

    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def makedirs(self, name, mode=0o777, exist_ok=False):  # type: (str, int, bool)->None
        raise NotImplementedError

    @abstractmethod
    def move(self, path, dest):  # type: (str, str) -> None
        raise NotImplementedError

    @abstractmethod
    def remove_file(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def remove(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def shutil_rmtree(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def has_sticky_bit(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def is_accessible(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def seems_to_have_delete_permissions(self, path):  # type: (str) -> int
        raise NotImplementedError

    @abstractmethod
    def read_file(self, path):  # type: (str) -> str
        raise NotImplementedError

    @abstractmethod
    def write_file(self, path, content):  # type: (str, str) -> None
        raise NotImplementedError

    @abstractmethod
    def get_mod(self, path):  # type: (str) -> int
        raise NotImplementedError

    @abstractmethod
    def path_lexists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError

    @abstractmethod
    def walk_no_follow(self,
                       top,  # type: str
                       ):  # type: (...) -> Iterable[Tuple[str, List[str], List[str]]]
        raise NotImplementedError

    @abstractmethod
    def rmdir(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def mkdtemp(self,
                prefix=None,  # type: Optional[str]
                suffix=None,  # type: Optional[str]
                dir=None,  # type: Optional[str]
                ):  # type: (...) -> str
        raise NotImplementedError

    def parent_realpath2(self, path):  # type: (str) -> str
        parent = os.path.dirname(path)
        return self.realpath(parent)

    def list_sorted(self, path):  # type: (str) -> List[str]
        return sorted(self.listdir(path))
