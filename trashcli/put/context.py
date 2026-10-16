import os
from typing import List
from typing import NamedTuple
from typing import Optional

from trashcli.compat import Protocol
from trashcli.lib.environ import Environ
from trashcli.put.core.logs import LogData
from trashcli.put.core.mode import Mode
from trashcli.put.core.trash_all_result import TrashAllResult
from trashcli.put.core.trash_result import TrashResult


class Context(NamedTuple('Context', [
    ('paths', List[str]),
    ('user_trash_dir', Optional[str]),
    ('mode', Mode),
    ('forced_volume', Optional[str]),
    ('home_fallback', bool),
    ('program_name', str),
    ('log_data', LogData),
    ('environ', Environ),
    ('uid', int),
])):
    def trash_each(self,
                   trasher,  # type: SingleTrasher
                   ):  # type (...) -> TrashAllResult
        failed_paths = []
        for path in self.paths:
            result = trasher.trash_single(without_trailing_slashes(path), self)
            if result == TrashResult.Failure:
                failed_paths.append(path)

        return TrashAllResult(failed_paths)


class SingleTrasher(Protocol):
    def trash_single(self,
                     path,  # type: str
                     context,  # type: 'Context'
                     ):
        raise NotImplementedError


def without_trailing_slashes(path):  # type: (str) -> str
    # a trailing slash hides "." and ".." and points at the wrong parent
    return path.rstrip(os.sep) or path
