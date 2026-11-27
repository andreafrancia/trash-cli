import os

from trashcli.restore.fs.protocols.path_reader_fs import PathReaderFs


class RealPathReaderFs(PathReaderFs):
    def path_exists(self, path):  # type: (str) -> bool
        return os.path.exists(path)

    def path_lexists(self, path):  # type: (str) -> bool
        return os.path.lexists(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return os.path.isdir(path)
