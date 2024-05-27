import os
import shutil
import stat
from typing import Iterable

from six import binary_type
from six import text_type

from trashcli.fs import AtomicWrite
from trashcli.fs import EntriesIfDirExists
from trashcli.fs import FileSize
from trashcli.fs import HasStickyBit
from trashcli.fs import IsStickyDir
from trashcli.fs import IsSymLink
from trashcli.fs import ListFilesInDir
from trashcli.fs import MakeFileExecutable
from trashcli.fs import MkDirs
from trashcli.fs import Move
from trashcli.fs import PathExists
from trashcli.fs import FileReader
from trashcli.fs import ReadCwd
from trashcli.fs import RemoveFile
from trashcli.fs import RemoveFile2
from trashcli.fs import RemoveFileIfExists
from trashcli.fs import WriteFile


class RealEntriesIfDirExists(EntriesIfDirExists):
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry


class RealPathExists(PathExists):
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


class RealFileReader(FileReader):
    def read_file(self, path):  # type: (...) -> binary_type
        with open(path, 'rb') as f:
            return f.read()

    def read_text_file(self, path):  # type: (...) -> text_type
        return self.read_file(path).decode('utf-8')


class RealWriteFile(WriteFile):
    def write_file(self, name,
                   contents,  # type: binary_type
                   ):  # type: (...) -> None
        with open(name, 'wb') as f:
            f.write(contents)

    def write_text_file(self, name,
                        contents,  # type: text_type
                        ):  # type: (...) -> None
        self.write_file(name, contents.encode('utf-8'))


class RealMakeFileExecutable(MakeFileExecutable):
    def make_file_executable(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)


class RealFileSize(FileSize):
    def file_size(self, path):
        return os.stat(path).st_size

class RealReasCwd(ReadCwd):
    def getcwd_as_realpath(self):
        return os.path.realpath(os.curdir)

