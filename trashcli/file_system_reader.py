from trashcli.fs import FsMethods
from trashcli.list.fs import FileSystemReaderForListCmd


class FileSystemReader(FileSystemReaderForListCmd):
    is_sticky_dir = FsMethods().is_sticky_dir
    is_symlink = FsMethods().is_symlink
    contents_of = FsMethods().contents_of
    entries_if_dir_exists = FsMethods().entries_if_dir_exists
    exists = FsMethods().exists
