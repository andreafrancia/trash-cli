from abc import abstractmethod
from typing import Iterable, Mapping

from trashcli.compat import Protocol


class VolumesListing(Protocol):
    @abstractmethod
    def list_volumes(self, environ):  # type: (Mapping[str, str]) -> Iterable[str]
        raise NotImplementedError()
