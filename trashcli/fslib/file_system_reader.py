from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.real.real_exists import RealExists
from trashcli.fslib.real.real_has_sticky_bit import RealHasStickyBit
from trashcli.fslib.real.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real.real_is_sym_link import RealIsSymLink
from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.list.fs import FileSystemReaderForListCmd


class FileSystemReader(FileSystemReaderForListCmd,
                       RealIsStickyDir,
                       RealHasStickyBit,
                       RealIsSymLink,
                       RealReadFile,
                       RealEntriesIfDirExists,
                       RealExists
                       ):
    pass
