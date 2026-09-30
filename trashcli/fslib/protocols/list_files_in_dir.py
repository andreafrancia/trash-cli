from typing import Iterable

from trashcli.compat import Protocol


class ListFilesInDir(Protocol):
    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        raise NotImplementedError()
