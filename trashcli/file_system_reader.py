from trashcli.fs import RealIsStickyDir, RealHasStickyBit, \
    RealIsSymLink, RealContentsOf, RealEntriesIfDirExists, RealExists
from trashcli.list.fs import FileSystemReaderForListCmd


class FileSystemReader(FileSystemReaderForListCmd,
                       RealIsStickyDir,
                       RealHasStickyBit,
                       RealIsSymLink,
                       RealContentsOf,
                       RealEntriesIfDirExists,
                       RealExists
                       ):
    pass
