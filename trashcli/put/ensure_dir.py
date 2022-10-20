from trashcli.put.fs import Fs


class EnsureDir:
    def __init__(self, fs): # type: (Fs) -> None
        self.fs = fs

    def ensure_dir(self, path, mode):
        if self.fs.isdir(path):
            self.fs.chmod(path, mode)
            return
        self.fs.makedirs(path, mode)
