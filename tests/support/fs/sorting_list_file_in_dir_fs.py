from trashcli.fslib.fs_operations import ListFilesInDir


class SortingListFilesInDir(ListFilesInDir):
    def __init__(self,
                 list_files_in_dir_fs,  # type: ListFilesInDir
                 ):
        self.list_files_in_dir_fs = list_files_in_dir_fs

    def list_files_in_dir(self, path):
        files = self.list_files_in_dir_fs.list_files_in_dir(path)
        return sorted(files)
