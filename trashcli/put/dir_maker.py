from trashcli.put.fs.fs import Fs


class DirMaker:
    def __init__(self, fs): # type: (Fs) -> None
        self.fs = fs

    def mkdir_p(self, path, mode):
        try:
            self.fs.makedirs(path, mode)
        except OSError:
            if not self.fs.isdir(path):
                raise
