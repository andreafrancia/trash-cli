from abc import abstractmethod
from typing import Iterable

from trashcli.compat import Protocol


class VolumesListing(Protocol):
    @abstractmethod
    def list_volumes(self, environ):  # type: (dict) -> Iterable[str]
        raise NotImplementedError()
