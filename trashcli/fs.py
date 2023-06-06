import os
import shutil
import stat
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


class ContentsOf(Protocol):
    @abstractmethod
    def contents_of(self, path):
        raise NotImplementedError()


class RealEntriesIfDirExists(EntriesIfDirExists):
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry


class RealExists(PathExists):
    def exists(self, path):  # type: (str) -> bool
        return os.path.exists(path)


class RealHasStickyBit(HasStickyBit):
    def has_sticky_bit(self, path):
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX


class RealIsStickyDir(IsStickyDir, RealHasStickyBit):
    def is_sticky_dir(self, path):  # type: (str) -> bool
        return os.path.isdir(path) and self.has_sticky_bit(path)


class RealIsSymLink(IsSymLink):
    def is_symlink(self, path):  # type: (str) -> bool
        return os.path.islink(path)


class RealContentsOf(ContentsOf):
    def contents_of(self, path):
        return _read_file(path)


class RealRemoveFile(RemoveFile):
    def remove_file(self, path):
        if os.path.lexists(path):
            try:
                os.remove(path)
            except:
                return shutil.rmtree(path)


class RealRemoveFile2(RemoveFile2):
    def remove_file2(self, path):
        try:
            os.remove(path)
        except OSError:
            shutil.rmtree(path)


class RealRemoveFileIfExists(RemoveFileIfExists, RemoveFile2):
    def remove_file_if_exists(self, path):
        if os.path.lexists(path): self.remove_file2(path)


class RealMove(Move):
    def move(self, path, dest):
        return shutil.move(path, str(dest))


class ListFilesInDir(Protocol):
    @abstractmethod
    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        raise NotImplementedError()


class RealListFilesInDir(ListFilesInDir):
    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        for entry in os.listdir(path):
            result = os.path.join(path, entry)
            yield result


class MkDirs(Protocol):
    @abstractmethod
    def mkdirs(self, path):
        raise NotImplementedError()


class RealMkDirs(MkDirs):
    def mkdirs(self, path):
        if os.path.isdir(path):
            return
        os.makedirs(path)


class AtomicWrite(Protocol):
    @abstractmethod
    def atomic_write(self, path, content):
        raise NotImplementedError()

    @abstractmethod
    def open_for_write_in_exclusive_and_create_mode(self, path):
        raise NotImplementedError()


class RealAtomicWrite(AtomicWrite):
    def atomic_write(self, path, content):
        file_handle = self.open_for_write_in_exclusive_and_create_mode(path)
        os.write(file_handle, content)
        os.close(file_handle)

    def open_for_write_in_exclusive_and_create_mode(self, path):
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)


class RealReadFile(ReadFile):
    def read_file(self, path):
        return _read_file(path)


class RealWriteFile(WriteFile):
    def write_file(self, name, contents):
        with open(name, 'w') as f:
            f.write(contents)


class RealMakeFileExecutable(MakeFileExecutable):
    def make_file_executable(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)


class RealFileSize(FileSize):
    def file_size(self, path):
        return os.stat(path).st_size


class FsMethods(
    RealEntriesIfDirExists,
    RealExists,
    RealIsStickyDir,
    RealIsSymLink,
    RealContentsOf,
    RealRemoveFile,
    RealRemoveFile2,
    RealRemoveFileIfExists,
    RealMove,
    RealListFilesInDir,
    RealMkDirs,
    RealAtomicWrite,
    RealReadFile,
    RealWriteFile,
    RealMakeFileExecutable,
    RealFileSize,
):
    pass


def _read_file(path):
    with open(path) as f:
        return f.read()


has_sticky_bit = RealHasStickyBit().has_sticky_bit
contents_of = RealContentsOf().contents_of
remove_file = RealRemoveFile().remove_file
move = RealMove().move
list_files_in_dir = RealListFilesInDir().list_files_in_dir
mkdirs = RealMkDirs().mkdirs
atomic_write = RealAtomicWrite().atomic_write
open_for_write_in_exclusive_and_create_mode = RealAtomicWrite().open_for_write_in_exclusive_and_create_mode
read_file = RealReadFile().read_file
write_file = RealWriteFile().write_file
make_file_executable = RealMakeFileExecutable().make_file_executable
file_size = RealFileSize().file_size
remove_file2 = RealRemoveFile2().remove_file2
is_sticky_dir = RealIsStickyDir().is_sticky_dir
