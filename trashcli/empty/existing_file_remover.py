from trashcli.fslib.fs_remove_file_if_exists import FsRemoveFileIfExists
from trashcli.fslib.protocols.fs import Fs
from trashcli.lib.trash_dir_remover import remove_in_trash_dir
from trashcli.fslib.protocols.remove_file2 import RemoveFile2
from trashcli.fslib.protocols.remove_file_if_exists import RemoveFileIfExists
from trashcli.fslib.fs_remove_file2 import FsRemoveFile2


class ExistingFileRemover(RemoveFileIfExists, RemoveFile2):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_file2(self, path):
        FsRemoveFile2(self.fs).remove_file2(path)

    def remove_file_if_exists(self, path):
        FsRemoveFileIfExists(self.fs).remove_file_if_exists(path)

    def remove_trash_entry(self, trash_dir, path):  # type: (str, str) -> None
        self.remove_file_if_exists(path)


class TrashDirFileRemover(ExistingFileRemover):
    def remove_trash_entry(self, trash_dir, path):  # type: (str, str) -> None
        if self.fs.path_lexists(path):
            remove_in_trash_dir(trash_dir, path)
