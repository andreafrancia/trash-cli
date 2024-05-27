from trashcli.fs_impl import RealFileReader
from trashcli.fs_impl import RealIsSymLink
from trashcli.fs_impl import RealIsStickyDir
from trashcli.fs_impl import RealHasStickyBit
from trashcli.fs_impl import RealPathExists
from trashcli.fs_impl import RealEntriesIfDirExists
from trashcli.list.fs import FileSystemReaderForListCmd


class FileSystemReader(FileSystemReaderForListCmd,
                       RealIsStickyDir,
                       RealHasStickyBit,
                       RealIsSymLink,
                       RealFileReader,
                       RealEntriesIfDirExists,
                       RealPathExists
                       ):
    pass
