from trashcli.lib.path_of_backup_copy import path_of_backup_copy


class AnotherProcessRemovesBeforeRead(object):
    """Wraps the reader of trash-rm or trash-empty.

    It acts like another process, for example another trash-rm, that removes
    a trashed file (its .trashinfo and its backup copy) after the command has
    listed the info dir and right before the command reads that .trashinfo.
    Everything else is done by the wrapped reader.
    """

    def __init__(self,
                 reader,  # the reader used by the command
                 fs,  # the file system seen by the other process
                 trashinfo_path,  # type: str
                 ):
        self.reader = reader
        self.fs = fs
        self.trashinfo_path = trashinfo_path

    def read_file(self, path):
        if path == self.trashinfo_path:
            self.fs.remove_file(path_of_backup_copy(path))
            self.fs.remove_file(path)
        return self.reader.read_file(path)

    def __getattr__(self, name):
        return getattr(self.reader, name)
