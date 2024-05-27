import abc

from six import add_metaclass

from trashcli.fs import FileReader
from trashcli.fs import IsSymLink
from trashcli.fs import IsStickyDir
from trashcli.fs import HasStickyBit
from trashcli.fs import PathExists
from trashcli.fs import EntriesIfDirExists


@add_metaclass(abc.ABCMeta)
class FileSystemReaderForListCmd(
    IsStickyDir,
    HasStickyBit,
    IsSymLink,
    FileReader,
    EntriesIfDirExists,
    PathExists,
):
    pass
