from trashcli.fslib.real_fs_operations import RealEntriesIfDirExists, RealExists
from trashcli.lib.dir_reader import DirReader


class FileSystemDirReader(DirReader,
                          RealEntriesIfDirExists,
                          RealExists,
                          ):
    pass
