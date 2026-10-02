from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.remove_file2 import RemoveFile2


class FsRemoveFile2(RemoveFile2):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_file2(self, path):
        try:
            self.fs.remove(path)
        except OSError:
            self.fs.shutil_rmtree(path)
