import os

from trashcli.fslib.protocols.entries_if_dir_exists import EntriesIfDirExists


class RealEntriesIfDirExists(EntriesIfDirExists):
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry
