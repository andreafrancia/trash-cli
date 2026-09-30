from trashcli.fslib.real.real_contents_of import RealContentsOf
from trashcli.restore.fs.protocols.file_reader_fs import FileReaderFs


class RealFileReaderFs(RealContentsOf, FileReaderFs):
    pass
