from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.real.real_exists import RealExists
from trashcli.lib.dir_reader import DirReader


class FileSystemDirReader(DirReader,
                          RealEntriesIfDirExists,
                          RealExists,
                          ):
    pass
