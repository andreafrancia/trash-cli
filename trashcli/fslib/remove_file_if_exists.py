from typing import Mapping, Callable
from abc import abstractmethod

from trashcli.compat import Protocol
from trashcli.fslib.force_remover import ForceRemover


class RemoveFileIfExists:
    def __init__(self,
                 fs,  # type: FsRemoveFileIfExistsFs
                 environ,  # type: Mapping[str, str]
                 geteuid,  # type: Callable[[], int]
                 ):  # type: (...) -> None
        self.fs = fs
        self.environ = environ
        self.geteuid = geteuid

    def remove_file_if_exists(self, path):
        if self.fs.path_lexists(path):
            ForceRemover(self.fs, self.environ,
                         self.geteuid).remove_path_forcefully(path)


class FsRemoveFileIfExistsFs(Protocol):
    @abstractmethod
    def path_lexists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def remove(self, path):  # type: (str) -> None
        raise NotImplementedError

    @abstractmethod
    def shutil_rmtree(self, path):  # type: (str) -> None
        raise NotImplementedError
