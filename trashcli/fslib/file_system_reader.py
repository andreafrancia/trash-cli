from trashcli.fslib.real_fs_operations import RealEntriesIfDirExists, RealExists, \
    RealIsSymLink, RealContentsOf
from trashcli.fslib.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real_has_sticky_bit import RealHasStickyBit
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
