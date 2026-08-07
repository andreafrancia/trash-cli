import os

from typing import Iterable

from trashcli.fslib.fs_operations import ListFilesInDir
from trashcli.restore.fs.file_reader_fs import FileReaderFs


class RestoreFakeFs(FileReaderFs, ListFilesInDir):
    def __init__(self,
                 fs,  # type FakeFs
                 ):
        self.fs = fs

    def contents_of(self, path):
        return self.fs.read(path)

    def list_files_in_dir(self, dir_path):  # type: (str) -> Iterable[str]
        for entry in self.fs.listdir(dir_path):
            result = os.path.join(dir_path, entry)
            yield result
