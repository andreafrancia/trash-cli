import os

from trashcli.restore.fs.path_reader_fs import PathReaderFs


class RealPathReaderFs(PathReaderFs):
    def path_exists(self, path):
        return os.path.exists(path)

    def path_lexists(self, path):
        return os.path.lexists(path)

    def path_isdir(self, path):
        return os.path.isdir(path)
