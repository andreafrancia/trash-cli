from trashcli.fslib.real_fs_operations import RealEntriesIfDirExists, RealExists, \
    RealIsSymLink, RealContentsOf
from trashcli.fslib.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real_read_sticky_bit_fs import RealReadStickyBitFs
from trashcli.list.fs import FileSystemReaderForListCmd


class FileSystemReader(FileSystemReaderForListCmd,
                       RealIsStickyDir,
                       RealReadStickyBitFs,
                       RealIsSymLink,
                       RealContentsOf,
                       RealEntriesIfDirExists,
                       RealExists
                       ):
    pass
