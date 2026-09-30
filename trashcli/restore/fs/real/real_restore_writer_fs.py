from trashcli.fslib.real.real_mk_dirs import RealMkDirs
from trashcli.fslib.real.real_move import RealMove
from trashcli.fslib.real.real_remove_file import RealRemoveFile
from trashcli.restore.fs.protocols.restore_writer_fs import RestoreWriterFs


class RealRestoreWriterFs(RestoreWriterFs):
    def mkdirs(self, path):
        return RealMkDirs().mkdirs(path)

    def move(self, path, dest):
        return RealMove().move(path, dest)

    def remove_file(self, path):
        return RealRemoveFile().remove_file(path)
