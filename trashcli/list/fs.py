import abc

from six import add_metaclass

from trashcli.fs import IsSymLink, ContentsOf, EntriesIfDirExists, PathExists, \
    IsStickyDir, HasStickyBit


@add_metaclass(abc.ABCMeta)
class FileSystemReaderForListCmd(
    IsStickyDir,
    HasStickyBit,
    IsSymLink,
    ContentsOf,
    EntriesIfDirExists,
    PathExists,
):
    pass
