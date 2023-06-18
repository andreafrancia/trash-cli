from typing import NamedTuple, Optional, Callable, Any, Iterable, List

from trashcli.restore.args import Sorter
from trashcli.restore.trashed_file import TrashedFile


class SortMethod(NamedTuple('SortMethod', [
    ('sort_func', Optional[Callable[[TrashedFile], Any]])
]), Sorter):

    def sort_files(self,
                   trashed_files,  # type: Iterable[TrashedFile]
                   ):  # type: (...) -> List[TrashedFile]
        if self.sort_func is None:
            return list(trashed_files)
        else:
            return sorted(trashed_files, key=self.sort_func)

    @classmethod
    def parse_sort_method(cls, sort_method):  # type: (str) -> 'SortMethod'
        sort_by_path = SortMethod(
            lambda x: x.original_location + str(x.deletion_date))
        sort_by_date = SortMethod(lambda x: x.deletion_date)
        do_not_sort = SortMethod(None)

        if sort_method == 'path':
            return sort_by_path
        elif sort_method == 'date':
            return sort_by_date
        else:
            return do_not_sort
