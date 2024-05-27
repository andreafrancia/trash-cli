from trashcli.fs import ReadCwd


class FakeReadCwd(ReadCwd):
    def __init__(self, default_cur_dir=None):
        self.default_cur_dir = default_cur_dir

    def chdir(self, path):
        self.default_cur_dir = path

    def getcwd_as_realpath(self):
        return self.default_cur_dir
