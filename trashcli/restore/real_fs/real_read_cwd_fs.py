import os

from trashcli.restore.fs.read_cwd_fs import ReadCwdFs


class RealReadCwdFs(ReadCwdFs):
    def getcwd_as_realpath(self):
        return os.path.realpath(os.curdir)
