from trashcli.fslib.protocols.entries_if_dir_exists import EntriesIfDirExists
from trashcli.fslib.protocols.fs import Fs


class RealEntriesIfDirExists(EntriesIfDirExists):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def entries_if_dir_exists(self, path):
        if self.fs.path_exists(path):
            for entry in self.fs.listdir(path):
                yield entry
