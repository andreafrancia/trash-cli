import os

from trashcli.fslib.fs_operations import RealMove
from trashcli.fslib.real_fs_operations import RealContentsOf, RealRemoveFile, \
    RealListFilesInDir, RealMkDirs
from trashcli.restore.restore_fs import FileReaderFs, RestoreReaderFs, \
    RestoreWriterFs, ReadCwdFs, ListingFs


class RealFileReaderFs(RealContentsOf, FileReaderFs):
    pass



class RealRestoreReaderFs(RestoreReaderFs):
    def path_exists(self, path):
        return os.path.exists(path)

    def path_lexists(self, path):
        return os.path.lexists(path)

    def path_isdir(self, path):
        return os.path.isdir(path)


class RealRestoreWriterFs(RestoreWriterFs):
    def mkdirs(self, path):
        return RealMkDirs().mkdirs(path)

    def move(self, path, dest):
        return RealMove().move(path, dest)

    def remove_file(self, path):
        return RealRemoveFile().remove_file(path)


class RealReadCwdFs(ReadCwdFs):
    def getcwd_as_realpath(self):
        return os.path.realpath(os.curdir)


class RealListingFs(ListingFs, RealListFilesInDir):
    pass
