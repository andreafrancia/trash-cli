from __future__ import absolute_import

from abc import abstractmethod
from typing import Iterable

from trashcli.compat import Protocol


class DirReaderFs(Protocol):
    @abstractmethod
    def entries_if_dir_exists(self, path):  # type: (str) -> Iterable[str]
        raise NotImplementedError

    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError
