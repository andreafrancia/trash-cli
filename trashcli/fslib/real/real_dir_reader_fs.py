from __future__ import absolute_import

from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.real.real_exists import RealExists


class RealDirReaderFs(RealEntriesIfDirExists, RealExists):
    pass
