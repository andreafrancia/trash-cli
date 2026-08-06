from trashcli.compat import Protocol


class PathReaderFs(Protocol):
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()

    def path_lexists(self, path):  # type: (str) -> bool
        return self.path_exists(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return False
