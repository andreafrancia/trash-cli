from trashcli.fslib.protocols.fs import Fs


class FakeTempfile:
    template = "tmp"
    def __init__(self, fs):
        self._counter = 0
        self.fs = fs

    def gettempdir(self):
        return "/tmp"

    def mkdtemp(self,
                suffix,  # type: str
                prefix,  # type: str
                dir,  # type: str
                ):
        import os
        self._counter += 1

        name = "{}{}{}".format(prefix, self._counter, suffix)
        if dir is None:
            dir = self.gettempdir()
            if not self.fs.path_isdir(dir):
                self.fs.mkdir(dir, mode=0o777)
                self.fs.set_sticky_bit(dir)

        full_path = os.path.join(dir, name)

        self.fs.mkdir(full_path, mode=0o700)

        return full_path
