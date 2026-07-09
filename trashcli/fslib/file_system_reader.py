from trashcli.fslib.real_fs_operations import RealEntriesIfDirExists, RealExists, \
    RealHasStickyBit, RealIsStickyDir, RealIsSymLink, RealContentsOf
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
