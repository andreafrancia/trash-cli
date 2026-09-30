import os
from typing import Iterable

from trashcli.fslib.protocols.fs import Fs


def list_all(fs, path):  # type: (Fs, str) -> Iterable[str]
    result = fs.walk_no_follow(path)
    for top, dirs, non_dirs in result:
        for d in dirs:
            yield os.path.join(top, d)
        for f in non_dirs:
            yield os.path.join(top, f)
