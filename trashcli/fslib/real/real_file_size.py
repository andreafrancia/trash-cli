import os

from trashcli.fslib.protocols.file_size import FileSize


class RealFileSize(FileSize):
    def file_size(self, path):
        return os.stat(path).st_size
