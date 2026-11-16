from trashcli.fslib.protocols.listdir_fs import ListdirFs


class SortingListdirFs(ListdirFs):
    def __init__(self,
                 list_files_in_dir_fs,  # type: ListdirFs
                 ):
        self.list_files_in_dir_fs = list_files_in_dir_fs

    def listdir(self, path):
        return sorted(self.list_files_in_dir_fs.listdir(path))