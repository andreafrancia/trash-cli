from trashcli.fs import FsMethods
from trashcli.lib.dir_reader import DirReader


class FileSystemDirReader(DirReader):
    entries_if_dir_exists = FsMethods().entries_if_dir_exists
    exists = FsMethods().exists
