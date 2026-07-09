from __future__ import absolute_import

from trashcli.compat import Protocol

from trashcli.fslib.fs_operations import EntriesIfDirExists, PathExists
from trashcli.fslib.real_fs_operations import RealEntriesIfDirExists, RealExists


class DirReader(
    EntriesIfDirExists,
    PathExists,
    Protocol,
):
    pass


class RealDirReader(RealEntriesIfDirExists, RealExists):
    pass
