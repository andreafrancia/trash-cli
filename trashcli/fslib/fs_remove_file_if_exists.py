from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.remove_file_if_exists import RemoveFileIfExists
from trashcli.fslib.real.real_remove_file2 import RealRemoveFile2


class FsRemoveFileIfExists(RemoveFileIfExists):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_file_if_exists(self, path):
        if self.fs.path_lexists(path):
            RealRemoveFile2(self.fs).remove_file2(path)
