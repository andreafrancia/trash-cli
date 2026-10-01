from typing import List

from trashcli.fslib.list_all import list_all
from trashcli.fslib.protocols.fs import Fs


def find_all(fs):  # type: (Fs) -> List[str]
    return list(list_all(fs, "/"))
