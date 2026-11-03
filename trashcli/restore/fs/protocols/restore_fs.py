from trashcli.fslib.protocols.listdir_fs import ListdirFs

from trashcli.compat import Protocol
from trashcli.fslib.protocols.volumes_fs import VolumesFs
from trashcli.restore.fs.protocols.file_reader_fs import FileReaderFs
from trashcli.restore.fs.protocols.path_reader_fs import PathReaderFs
from trashcli.restore.fs.protocols.read_cwd_fs import ReadCwdFs
from trashcli.restore.fs.protocols.restore_writer_fs import RestoreWriterFs


class RestoreFs(ListdirFs,
                FileReaderFs,
                PathReaderFs,
                ReadCwdFs,
                VolumesFs,
                RestoreWriterFs,
                Protocol):
    pass
