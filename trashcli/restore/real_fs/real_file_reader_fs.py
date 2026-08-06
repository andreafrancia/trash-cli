from trashcli.fslib.real_fs_operations import RealContentsOf
from trashcli.restore.fs.file_reader_fs import FileReaderFs


class RealFileReaderFs(RealContentsOf, FileReaderFs):
    pass
