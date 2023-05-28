from trashcli.fs import RealExists, RealEntriesIfDirExists
from trashcli.lib.dir_reader import DirReader


class FileSystemDirReader(DirReader,
                          RealEntriesIfDirExists,
                          RealExists,
                          ):
    pass
