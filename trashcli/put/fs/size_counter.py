import os

from six.moves import map as imap

from trashcli.put.fs.fs import Fs


class SizeCounter:
    def __init__(self,
                 fs,  # type: Fs
                 ):
        self.fs = fs

    def get_size_recursive(self, path):
        if self.fs.isfile(path):
            return self.fs.getsize(path)

        files = self.list_all_files(path)
        files_sizes = imap(self.fs.getsize, files)
        return sum(files_sizes, 0)

    def list_all_files(self,
                       path,  # type: str
                       ):
        for path, dirs, files in self.fs.walk_no_follow(path):
            for f in files:
                yield os.path.join(path, f)
