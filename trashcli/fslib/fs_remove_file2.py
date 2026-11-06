import os

from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.remove_file2 import RemoveFile2

# the permissions on a dir that are needed to unlink its entries
WRITE_AND_SEARCH = 0o300


class FsRemoveFile2(RemoveFile2):
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_file2(self, path):
        try:
            self.fs.remove(path)
        except OSError:
            try:
                self.fs.shutil_rmtree(path)
            except OSError:
                # e.g. a dir containing a read-only dir (#364)
                FsRemoveTreeMakingDirsWritable(self.fs).remove_tree(path)


class FsRemoveTreeMakingDirsWritable:
    """Removes a dir with its content, adding to each dir of the tree the
    write and search permissions for the owner when they are missing.

    It is meant to delete a trashed dir for good: the permissions are changed
    only on the dirs that are being removed, never on the files (their
    permissions do not matter to unlink them), never on the targets of the
    symlinks, never on the parent of the removed dir. The read permission is
    not added, so an unreadable dir is still an error.
    """

    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs

    def remove_tree(self, path):  # type: (str) -> None
        if self.fs.is_symlink(path) or not self.fs.path_isdir(path):
            self.fs.remove(path)
            return
        self._make_writable_and_searchable(path)
        for name in self.fs.listdir(path):
            self.remove_tree(os.path.join(path, name))
        self.fs.rmdir(path)

    def _make_writable_and_searchable(self, path):  # type: (str) -> None
        mode = self.fs.get_mod(path)
        if mode & WRITE_AND_SEARCH != WRITE_AND_SEARCH:
            self.fs.chmod(path, mode | WRITE_AND_SEARCH)
