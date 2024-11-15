import os
import tempfile

from trashcli.path import Path
from trashcli.put.fs.fs import list_all
from trashcli.put.fs.real_fs import RealFs


class MyPath(Path):
    def __new__(cls, path, *args, **kwargs):
        # explicitly only pass value to the str constructor
        return super(MyPath, cls).__new__(cls, path)

    def __init__(self, path):
        super(MyPath, self).__init__(path)
        self.fs = RealFs()

    def existence_of(self, *paths):
        return [self.existence_of_single(p) for p in paths]

    def existence_of_single(self, path):  # type: (MyPath) -> str
        path = self / path
        existence = self.fs.exists(path)
        existence_message = {
            True: "exists",
            False: "does not exist"
        }[existence]
        return "%s: %s" % (path.replace(self, ''), existence_message)

    def mkdir_rel(self, path):
        self.fs.mkdir(self / path)
        return self / path

    def symlink_rel(self, src, dest):
        self.fs.symlink(self / src, self / dest)

    def list_dir_rel(self):
        return self.fs.listdir(self)

    @property
    def parent(self):  # type: (...) -> MyPath
        return MyPath(os.path.dirname(self))

    def clean_up(self):
        self.fs.rmtree(self)

    @classmethod
    def make_temp_dir(cls):
        return cls(os.path.realpath(tempfile.mkdtemp(suffix="_trash_cli_test")))

    def list_all_files_sorted(self):
        return sorted([p.replace(self, '')
                       for p in list_all(self.fs, self)])
