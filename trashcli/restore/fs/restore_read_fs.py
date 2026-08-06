from trashcli.compat import Protocol
from trashcli.fslib.fs_operations import ListFilesInDir
from trashcli.fstab.volumes import Volumes
from trashcli.restore.fs.file_reader_fs import FileReaderFs
from trashcli.restore.fs.path_reader_fs import PathReaderFs
from trashcli.restore.fs.read_cwd_fs import ReadCwdFs


class RestoreReadFs(ListFilesInDir,
                    FileReaderFs,
                    PathReaderFs,
                    ReadCwdFs,
                    Volumes,
                    Protocol):
    pass
