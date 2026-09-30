from abc import abstractmethod
from typing import List

from trashcli.compat import Protocol


class EntriesIfDirExists(Protocol):
    @abstractmethod
    def entries_if_dir_exists(self, path):  # type: (str) -> List[str]
        raise NotImplementedError()
