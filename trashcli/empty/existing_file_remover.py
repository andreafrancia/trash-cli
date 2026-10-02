from trashcli.fslib.fs_remove_file_if_exists import FsRemoveFileIfExists
from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.remove_file2 import RemoveFile2
from trashcli.fslib.protocols.remove_file_if_exists import RemoveFileIfExists
from trashcli.fslib.real.real_remove_file2 import RealRemoveFile2


class ExistingFileRemover(RemoveFileIfExists, RemoveFile2):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_file2(self, path):
        RealRemoveFile2(self.fs).remove_file2(path)

    def remove_file_if_exists(self, path):
        FsRemoveFileIfExists(self.fs).remove_file_if_exists(path)
