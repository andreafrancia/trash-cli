from abc import abstractmethod
from typing import Iterable

from trashcli.compat import Protocol


class EntriesIfDirExists(Protocol):
    @abstractmethod
    def entries_if_dir_exists(self, path):  # type: (str) -> Iterable[str]
        raise NotImplementedError()
