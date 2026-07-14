from abc import abstractmethod, ABCMeta

import six

from trashcli.compat import Protocol
from trashcli.fslib.fs_operations import ListFilesInDir


class ListingFs(ListFilesInDir, Protocol):
    pass


class FileReaderFs(Protocol):
    @abstractmethod
    def contents_of(self, path):
        raise NotImplementedError()


@six.add_metaclass(ABCMeta)
class RestoreReaderFs:
    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()

    def path_lexists(self, path):  # type: (str) -> bool
        return self.path_exists(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return False


@six.add_metaclass(ABCMeta)
class RestoreWriterFs:
    @abstractmethod
    def mkdirs(self, path):  # type: (str) -> None
        raise NotImplementedError()

    @abstractmethod
    def move(self, path, dest):  # type: (str, str) -> None
        raise NotImplementedError()

    @abstractmethod
    def remove_file(self, path):  # type: (str) -> None
        raise NotImplementedError()


@six.add_metaclass(ABCMeta)
class ReadCwdFs:
    @abstractmethod
    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError()
