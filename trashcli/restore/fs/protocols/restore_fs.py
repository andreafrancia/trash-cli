from typing import List

from trashcli.compat import Protocol

class RestoreFs(Protocol):

    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError

    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError

    def list_mount_points(self):  # type: () -> List[str]
        raise NotImplementedError

    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    def path_lexists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    def read_file(self, path):  # type: (str) -> str
        raise NotImplementedError

    def remove_file(self, path):  # type: (str) -> None
        raise NotImplementedError

    def shutil_move(self, src, dst):  # type: (str, str) -> None
        raise NotImplementedError

    def volume_of(self, path):  # type: (str) -> str
        raise NotImplementedError

    def path_isdir(self, path):  # type: (str) -> bool
        raise NotImplementedError

