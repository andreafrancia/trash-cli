import abc

from six import add_metaclass

from trashcli.fslib.protocols.is_sym_link import IsSymLink
from trashcli.fslib.protocols.contents_of import ContentsOf
from trashcli.fslib.protocols.entries_if_dir_exists import EntriesIfDirExists
from trashcli.fslib.protocols.path_exists import PathExists
from trashcli.fslib.protocols.is_sticky_dir import IsStickyDir
from trashcli.fslib.protocols.has_sticky_bit import HasStickyBit


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
