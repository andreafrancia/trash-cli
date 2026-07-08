import datetime
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
        # materialise, like SortFunction: the caller len()s and re-iterates it
        return list(trashed_files)


class SortFunction(Sorter):
    def __init__(self,
                 sort_func):  # type: (Callable[[TrashedFile], Any]) -> None
        self.sort_func = sort_func

    def sort_files(self, trashed_files,  # type: Iterable[TrashedFile]
                   ):  # type: (...) -> Iterable[TrashedFile]
        return sorted(trashed_files, key=self.sort_func)


def sorter_for(sort,  # type: Sort
               ):  # type (...) -> Sorter

    def date_ranking(x):
        # a missing/unparsable date is None; sort it first instead of crashing
        return x.deletion_date or datetime.datetime.min

    path_ranking = lambda x: (x.original_location, date_ranking(x))
    return {
        Sort.ByPath: SortFunction(path_ranking),
        Sort.ByDate: SortFunction(date_ranking),
        Sort.DoNot: NoSorter(),
    }[sort]
