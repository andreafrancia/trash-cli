from trashcli.fslib.protocols.dir_reader_fs import DirReaderFs
from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.real.real_exists import RealExists


class FileSystemDirReader(DirReaderFs,
                          RealExists,
                          ):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def entries_if_dir_exists(self, path):
        return RealEntriesIfDirExists(self.fs).entries_if_dir_exists(path)
