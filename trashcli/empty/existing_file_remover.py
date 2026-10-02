from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.real.real_remove_file2 import RealRemoveFile2
from trashcli.fslib.real.real_remove_file_if_exists import RealRemoveFileIfExists


class ExistingFileRemover(RealRemoveFileIfExists):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_file2(self, path):
        RealRemoveFile2(self.fs).remove_file2(path)
