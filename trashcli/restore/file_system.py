import os
from abc import ABCMeta, abstractmethod
from trashcli.compat import Protocol

import six

from trashcli import fs
from trashcli.fs import FsMethods, RealListFilesInDir, ListFilesInDir, \
    RealContentsOf


class FileReader(Protocol):
    @abstractmethod
    def contents_of(self, path):
        raise NotImplementedError()


class RealFileReader(RealContentsOf, FileReader):
    pass


class FakeFileReader(FileReader):
    def __init__(self, contents=None):
        self.contents = contents

    def set_content(self, contents):
        self.contents = contents

    def contents_of(self, path):
        return self.contents


@six.add_metaclass(ABCMeta)
class RestoreReadFileSystem:
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()


class RealRestoreReadFileSystem(RestoreReadFileSystem):
    def path_exists(self, path):
        return os.path.exists(path)


@six.add_metaclass(ABCMeta)
class RestoreWriteFileSystem:
    @abstractmethod
    def mkdirs(self, path):  # type: (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def move(self, path, dest):  # type: (str, str) -> None
        raise NotImplementedError()

    @abstractmethod
    def remove_file(self, path):  # type: (str) -> None
        raise NotImplementedError()


class RealRestoreWriteFileSystem(RestoreWriteFileSystem):
    def mkdirs(self, path):
        return fs.mkdirs(path)

    def move(self, path, dest):
        return fs.move(path, dest)

    def remove_file(self, path):
        return fs.remove_file(path)


@six.add_metaclass(ABCMeta)
class ReadCwd:
    @abstractmethod
    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError()


class RealReadCwd(ReadCwd):
    def getcwd_as_realpath(self):
        return os.path.realpath(os.curdir)


class FakeReadCwd(ReadCwd):
    def __init__(self, default_cur_dir=None):
        self.default_cur_dir = default_cur_dir

    def chdir(self, path):
        self.default_cur_dir = path

    def getcwd_as_realpath(self):
        return self.default_cur_dir


class ListingFileSystem(ListFilesInDir, Protocol):
    pass


class RealListingFileSystem(ListingFileSystem, RealListFilesInDir):
    pass
