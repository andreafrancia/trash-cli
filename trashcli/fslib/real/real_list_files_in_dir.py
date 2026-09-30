import os

from typing import Iterable

from trashcli.fslib.protocols.list_files_in_dir import ListFilesInDir


class RealListFilesInDir(ListFilesInDir):
    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        for entry in os.listdir(path):
            result = os.path.join(path, entry)
            yield result
