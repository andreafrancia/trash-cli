from trashcli.fslib.real.real_list_files_in_dir import RealListdirFs
from trashcli.fslib.real.real_mk_dirs import RealMkDirs
from trashcli.fslib.real.real_move import RealMove
from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.fslib.real.real_remove_file import RealRemoveFile
from trashcli.fslib.real.real_volumes import RealVolumesFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_read_cwd_fs import RealReadCwdFs


class RealRestoreFs:
    def __init__(self):
        self.listdir = RealListdirFs().listdir
        self.read_file = RealReadFile().read_file
        self.path_exists = RealPathReaderFs().path_exists
        self.path_lexists = RealPathReaderFs().path_lexists
        self.path_isdir = RealPathReaderFs().path_isdir
        self.volume_of = RealVolumesFs().volume_of
        self.list_mount_points = RealVolumesFs().list_mount_points
        self.getcwd_as_realpath = RealReadCwdFs().getcwd_as_realpath
        self.mkdirs = RealMkDirs().mkdirs
        self.move = RealMove().move
        self.remove_file = RealRemoveFile().remove_file
