import os

from typing import Iterable

from trashcli.restore.restore_fs import FileReaderFs
from trashcli.restore.real_restore_fs import ListingFs


class RestoreFakeFs(FileReaderFs, ListingFs):
    def __init__(self,
                 fs,  # type FakeFs
                 ):
        self.fs = fs

    def contents_of(self, path):
        return self.fs.read(path)

    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        for entry in self.fs.listdir(path):
            result = os.path.join(path, entry)
            yield result
