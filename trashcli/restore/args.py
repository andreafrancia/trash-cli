from typing import Iterable, List, NamedTuple, Optional

from trashcli.compat import Protocol
from trashcli.restore.trashed_file import TrashedFile


class Sorter(Protocol):
    def sort_files(self,
                   trashed_files,  # type: Iterable[TrashedFile]
                   ):  # type: (...) -> List[TrashedFile]
        raise NotImplementedError()


class RunRestoreArgs(
    NamedTuple('RunRestoreArgs', [
        ('path', str),
        ('sort', Sorter),
        ('trash_dir', Optional[str]),
        ('overwrite', bool),
    ])):
    pass
