from typing import List, Tuple

from trashcli.fslib.list_all import list_all
from trashcli.fslib.protocols.fs import Fs


def read_all_files(fs, path):  # type: (Fs, str) -> List[Tuple[str, str]]
    return [(f, fs.read_file(f))
            for f in list_all(fs, path)
            if fs.isfile(f)]
