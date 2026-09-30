from __future__ import absolute_import

from trashcli.compat import Protocol

from trashcli.fslib.protocols.entries_if_dir_exists import EntriesIfDirExists
from trashcli.fslib.protocols.path_exists import PathExists
from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.real.real_exists import RealExists


class DirReader(
    EntriesIfDirExists,
    PathExists,
    Protocol,
):
    pass


class RealDirReader(RealEntriesIfDirExists, RealExists):
    pass
