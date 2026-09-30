from __future__ import absolute_import

from trashcli.compat import Protocol

from trashcli.fslib.protocols.entries_if_dir_exists import EntriesIfDirExists
from trashcli.fslib.protocols.path_exists import PathExists


class DirReaderFs(
    EntriesIfDirExists,
    PathExists,
    Protocol,
):
    pass
