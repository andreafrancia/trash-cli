from __future__ import absolute_import

from trashcli.compat import Protocol

from trashcli.fs import EntriesIfDirExists, PathExists, RealEntriesIfDirExists, \
    RealExists


class DirReader(
    EntriesIfDirExists,
    PathExists,
    Protocol,
):
    pass


class RealDirReader(RealEntriesIfDirExists, RealExists):
    pass
