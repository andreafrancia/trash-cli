from typing import List

from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.listdir_fs import ListdirFs


class SortingListdirFs(ListdirFs):
    def __init__(self,
                 list_files_in_dir_fs,  # type: ListdirFs
                 ):
        self.list_files_in_dir_fs = list_files_in_dir_fs

    def listdir(self, path):
        return sorted(self.list_files_in_dir_fs.listdir(path))

def make_listdir_sorted(fs): # type: (Fs) -> None
    old_list_dir = fs.listdir
    def sorted_list_dir(path):  # type: (str) -> List[str]
        return sorted(old_list_dir(path))
    fs.listdir = sorted_list_dir  # type: ignore[method-assign]
