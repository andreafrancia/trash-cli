import shutil
from abc import abstractmethod

from typing import Iterable, List
from trashcli.compat import Protocol


class FileSize(Protocol):
    @abstractmethod
    def file_size(self, path):
        raise NotImplementedError()


class MakeFileExecutable(Protocol):
    @abstractmethod
    def make_file_executable(self, path):
        raise NotImplementedError()


class WriteFile(Protocol):
    @abstractmethod
    def write_file(self, name, contents):
        raise NotImplementedError()


class ReadFile(Protocol):
    @abstractmethod
    def read_file(self, path):
        raise NotImplementedError()


class Move(Protocol):
    @abstractmethod
    def move(self, path, dest):
        raise NotImplementedError()


class RemoveFile2(Protocol):
    @abstractmethod
    def remove_file2(self, path):
        raise NotImplementedError()


class RemoveFile(Protocol):
    @abstractmethod
    def remove_file(self, path):
        raise NotImplementedError()


class RemoveFileIfExists(Protocol):
    @abstractmethod
    def remove_file_if_exists(self, path):
        raise NotImplementedError()


class EntriesIfDirExists(Protocol):
    @abstractmethod
    def entries_if_dir_exists(self, path):  # type: (str) -> List[str]
        raise NotImplementedError()


class PathExists(Protocol):
    @abstractmethod
    def exists(self, path):
        raise NotImplementedError()


class HasStickyBit(Protocol):
    @abstractmethod
    def has_sticky_bit(self, path):  # type: (str) -> bool
        raise NotImplementedError


class IsStickyDir(Protocol):
    @abstractmethod
    def is_sticky_dir(self, path):  # type: (str) -> bool
        raise NotImplementedError


class IsSymLink(Protocol):
    @abstractmethod
    def is_symlink(self, path):  # type: (str) -> bool
        raise NotImplementedError


class IsWorldWritable(Protocol):
    @abstractmethod
    def is_world_writable(self, path):  # type: (str) -> bool
        raise NotImplementedError


class ContentsOf(Protocol):
    @abstractmethod
    def contents_of(self, path):
        raise NotImplementedError()


class RealMove(Move):
    def move(self, path, dest):
        return shutil.move(path, str(dest))


class ListFilesInDir(Protocol):
    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        raise NotImplementedError()


class MkDirs(Protocol):
    @abstractmethod
    def mkdirs(self, path):
        raise NotImplementedError()


class AtomicWrite(Protocol):
    @abstractmethod
    def atomic_write(self, path, content):
        raise NotImplementedError()

    @abstractmethod
    def open_for_write_in_exclusive_and_create_mode(self, path):
        raise NotImplementedError()


