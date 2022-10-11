class EnsureDir:
    def __init__(self, fs):
        self.fs = fs

    def ensure_dir(self, path, mode):
        if self.fs.isdir(path):
            self.fs.chmod(path, mode)
            return
        self.fs.makedirs(path, mode)
