from typing import Callable, Mapping

from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.remove_file_if_exists import RemoveFileIfExists
from trashcli.fslib.force_remove_impl import ForceRemoverImpl


class FsRemoveFileIfExists(RemoveFileIfExists):
    def __init__(self,
                 fs,  # type: Fs
                 environ,  # type: Mapping[str, str]
                 geteuid,  # type: Callable[[], int]
                 ):  # type: (...) -> None
        self.fs = fs
        self.environ = environ
        self.geteuid = geteuid

    def remove_file_if_exists(self, path):
        if self.fs.path_lexists(path):
            ForceRemoverImpl(self.fs, self.environ, self.geteuid).remove_file2(path)
