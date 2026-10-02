from trashcli.compat import Protocol
from trashcli.fslib.protocols.list_files_in_dir import ListFilesInDir
from trashcli.fslib.protocols.volumes_fs import VolumesFs
from trashcli.restore.fs.protocols.file_reader_fs import FileReaderFs
from trashcli.restore.fs.protocols.path_reader_fs import PathReaderFs
from trashcli.restore.fs.protocols.read_cwd_fs import ReadCwdFs


class RestoreReadFs(ListFilesInDir,
                    FileReaderFs,
                    PathReaderFs,
                    ReadCwdFs,
                    VolumesFs,
                    Protocol):
    pass
