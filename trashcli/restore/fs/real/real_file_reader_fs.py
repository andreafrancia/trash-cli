from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.restore.fs.protocols.file_reader_fs import FileReaderFs


class RealFileReaderFs(RealReadFile, FileReaderFs):
    pass
