from abc import abstractmethod
from typing import Callable, Any, Iterable

from trashcli.compat import Protocol
from trashcli.restore.args import Sort
from trashcli.restore.trashed_file import TrashedFile


def sort_files(sort,  # type: Sort
               trashed_files,  # type: Iterable[TrashedFile]
               ):  # type: (...) -> Iterable[TrashedFile]
    return sorter_for(sort).sort_files(trashed_files)


class Sorter(Protocol):
    @abstractmethod
    def sort_files(self, trashed_files,  # type: Iterable[TrashedFile]
                   ):  # type: (...) -> Iterable[TrashedFile]
        raise NotImplementedError()


class NoSorter(Sorter):
    def sort_files(self, trashed_files,  # type: Iterable[TrashedFile]
                   ):  # type: (...) -> Iterable[TrashedFile]
        return trashed_files


class SortFunction(Sorter):
    def __init__(self,
                 sort_func):  # type: (Callable[[TrashedFile], Any]) -> None
        self.sort_func = sort_func

    def sort_files(self, trashed_files,  # type: Iterable[TrashedFile]
                   ):  # type: (...) -> Iterable[TrashedFile]
        return sorted(trashed_files, key=self.sort_func)


def sorter_for(sort,  # type: Sort
               ):  # type (...) -> Sorter

    path_ranking = lambda x: x.original_location + str(x.deletion_date)
    date_rankking = lambda x: x.deletion_date
    return {
        Sort.ByPath: SortFunction(path_ranking),
        Sort.ByDate: SortFunction(date_rankking),
        Sort.DoNot: NoSorter,
    }[sort]
