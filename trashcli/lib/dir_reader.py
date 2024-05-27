from __future__ import absolute_import

from trashcli.compat import Protocol

from trashcli.fs_impl import RealPathExists
from trashcli.fs_impl import RealEntriesIfDirExists
from trashcli.fs import PathExists
from trashcli.fs import EntriesIfDirExists


class DirReader(
    EntriesIfDirExists,
    PathExists,
    Protocol,
):
    pass


class RealDirReader(RealEntriesIfDirExists, RealPathExists):
    pass
