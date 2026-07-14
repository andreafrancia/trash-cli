from trashcli.compat import Protocol
from trashcli.fslib.fs_operations import ListFilesInDir
from trashcli.fstab.volumes import Volumes


class FileReaderFs(Protocol):
    def contents_of(self, path):
        raise NotImplementedError()


class PathReaderFs(Protocol):
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()

    def path_lexists(self, path):  # type: (str) -> bool
        return self.path_exists(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return False


class ReadCwdFs(Protocol):
    def getcwd_as_realpath(self):  # type: () -> str
        raise NotImplementedError()


class RestoreReadFs(ListFilesInDir,
                    FileReaderFs,
                    PathReaderFs,
                    ReadCwdFs,
                    Volumes,
                    Protocol):
    pass


class RestoreWriterFs(Protocol):
    def mkdirs(self, path):  # type: (str) -> None
        raise NotImplementedError()

    def move(self, path, dest):  # type: (str, str) -> None
        raise NotImplementedError()

    def remove_file(self, path):  # type: (str) -> None
        raise NotImplementedError()
