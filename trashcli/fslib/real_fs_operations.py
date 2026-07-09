import os
import shutil
import stat
from typing import Iterable

from trashcli.fslib.fs_operations import EntriesIfDirExists, PathExists, HasStickyBit, \
    IsStickyDir, IsSymLink, IsWorldWritable, ContentsOf, RemoveFile, \
    RemoveFile2, RemoveFileIfExists, ListFilesInDir, MkDirs, AtomicWrite, \
    ReadFile, WriteFile, MakeFileExecutable, FileSize


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


class RealIsWorldWritable(IsWorldWritable):
    def is_world_writable(self, path):  # type: (str) -> bool
        try:
            return bool(os.stat(path).st_mode & stat.S_IWOTH)
        except OSError:
            return False


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


class RealListFilesInDir(ListFilesInDir):
    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        for entry in os.listdir(path):
            result = os.path.join(path, entry)
            yield result


class RealMkDirs(MkDirs):
    def mkdirs(self, path):
        if os.path.isdir(path):
            return
        os.makedirs(path)


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


def _read_file(path):
    with open(path) as f:
        return f.read()
