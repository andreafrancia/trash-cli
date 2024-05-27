from trashcli.compat import Protocol


class ScriptFs(Protocol):
    def write_file(self, name, contents):
        raise NotImplementedError

    def make_file_executable(self, path):
        raise NotImplementedError
