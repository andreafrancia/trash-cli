from __future__ import absolute_import

from typing import Protocol

from trashcli.fs import EntriesIfDirExists, PathExists


class DirReader(
    EntriesIfDirExists,
    PathExists,
    Protocol,
):
    pass
