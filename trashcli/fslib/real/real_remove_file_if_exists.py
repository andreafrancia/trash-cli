import os

from trashcli.fslib.protocols.remove_file2 import RemoveFile2
from trashcli.fslib.protocols.remove_file_if_exists import RemoveFileIfExists


class RealRemoveFileIfExists(RemoveFileIfExists, RemoveFile2):
    def remove_file_if_exists(self, path):
        if os.path.lexists(path): self.remove_file2(path)
