from typing import List

from trashcli.fslib.real.real_move import RealShUtilMove
from trashcli.fslib.real.real_remove_file import RealRemoveFile
from trashcli.fslib.real.real_volumes import RealVolumesFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.compat import Protocol

class RestoreFs(Protocol):

    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError

    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError

    def list_mount_points(self):  # type: () -> List[str]
        raise NotImplementedError

    def read_file(self, path):  # type: (str) -> str
        raise NotImplementedError

    def __init__(self):
        self.shutil_move = RealShUtilMove().shutil_move
        self.path_exists = RealPathReaderFs().path_exists
        self.path_lexists = RealPathReaderFs().path_lexists
        self.path_isdir = RealPathReaderFs().path_isdir
        self.remove_file = RealRemoveFile().remove_file
        self.volume_of = RealVolumesFs().volume_of

