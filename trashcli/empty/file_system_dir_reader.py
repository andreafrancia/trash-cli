from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.real.real_exists import RealExists
from trashcli.fslib.protocols.dir_reader_fs import DirReaderFs


class FileSystemDirReader(DirReaderFs,
                          RealEntriesIfDirExists,
                          RealExists,
                          ):
    pass
