import os

from trashcli.fslib.protocols.is_sym_link import IsSymLink


class RealIsSymLink(IsSymLink):
    def is_symlink(self, path):  # type: (str) -> bool
        return os.path.islink(path)
