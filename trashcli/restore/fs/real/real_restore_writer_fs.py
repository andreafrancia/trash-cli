from trashcli.fslib.real.real_mk_dirs import RealMkDirs
from trashcli.fslib.clean_move import clean_move
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_remove_file import RealRemoveFile
from trashcli.restore.fs.protocols.restore_writer_fs import RestoreWriterFs


class RealRestoreWriterFs(RestoreWriterFs):
    def mkdirs(self, path):
        return RealMkDirs().mkdirs(path)

    def move(self, path, dest):
        clean_move(RealFs(), path, dest)

    def remove_file(self, path):
        return RealRemoveFile().remove_file(path)
