import os
from typing import Iterable

from trashcli.fslib.protocols.listdir_fs import ListdirFs


def listdir_with_complete_path(
        fs,   # type: ListdirFs
        path,   # type: str
):  # type: (...) -> Iterable[str]
    for entry in fs.listdir(path):
        yield os.path.join(path, entry)
