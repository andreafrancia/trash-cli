from trashcli.compat import Protocol
from trashcli.restore.fs.protocols.restore_read_fs import RestoreReadFs
from trashcli.restore.fs.protocols.restore_writer_fs import RestoreWriterFs


class RestoreFs(RestoreReadFs,
                RestoreWriterFs,
                Protocol):
    pass
