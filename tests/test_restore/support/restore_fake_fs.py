import os

from typing import Iterable

from tests.support.fakes.fake_volume_path_fs import FakeVolumePathFs
from trashcli.fslib.protocols.list_files_in_dir import ListFilesInDir
from trashcli.restore.restore_fs import FileReaderFs


class RestoreFakeFs(FileReaderFs, ListFilesInDir, FakeVolumePathFs):
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
