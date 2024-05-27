from trashcli.fs_impl import RealPathExists
from trashcli.fs_impl import RealEntriesIfDirExists
from trashcli.lib.dir_reader import DirReader


class FileSystemDirReader(DirReader,
                          RealEntriesIfDirExists,
                          RealPathExists,
                          ):
    pass
