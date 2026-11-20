from typing import List

from trashcli.fslib.real.real_list_files_in_dir import RealListdirFs
from trashcli.fslib.real.real_mk_dirs import RealMkDirs
from trashcli.fslib.real.real_move import RealMove
from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.fslib.real.real_remove_file import RealRemoveFile
from trashcli.fslib.real.real_volumes import RealVolumesFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_read_cwd_fs import RealReadCwdFs
from trashcli.compat import Protocol

class RestoreFs(Protocol):

    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError

    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError


    def __init__(self):
        self.list_mount_points = RealVolumesFs().list_mount_points
        self.read_file = RealReadFile().read_file
        self.mkdirs = RealMkDirs().mkdirs
        self.move = RealMove().move
        self.path_exists = RealPathReaderFs().path_exists
        self.path_lexists = RealPathReaderFs().path_lexists
        self.path_isdir = RealPathReaderFs().path_isdir
        self.remove_file = RealRemoveFile().remove_file
        self.volume_of = RealVolumesFs().volume_of

