from trashcli.fslib.fs_operations import RealMove
from trashcli.fslib.real_fs_operations import RealMkDirs, RealRemoveFile
from trashcli.restore.fs.restore_write_fs import RestoreWriterFs


class RealRestoreWriterFs(RestoreWriterFs):
    def mkdirs(self, path):
        return RealMkDirs().mkdirs(path)

    def move(self, path, dest):
        return RealMove().move(path, dest)

    def remove_file(self, path):
        return RealRemoveFile().remove_file(path)
