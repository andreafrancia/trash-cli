import abc

from six import add_metaclass

from trashcli.fslib.fs_operations import IsSymLink, ContentsOf, EntriesIfDirExists, PathExists
from trashcli.fslib.is_sticky_dir import IsStickyDir


@add_metaclass(abc.ABCMeta)
class FileSystemReaderForListCmd(
    IsStickyDir,
    IsSymLink,
    ContentsOf,
    EntriesIfDirExists,
    PathExists,
):
    pass
