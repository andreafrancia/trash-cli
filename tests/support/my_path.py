import os
import shutil
import tempfile

from trashcli.put.fs.real_fs import RealFs
from trashcli.put.fs.fs import list_all


class MyPath(str):

    def __truediv__(self, other_path):
        return self.path_join(other_path)

    def __div__(self, other_path):
        return self.path_join(other_path)

    def path_join(self, other_path):
        return MyPath(os.path.join(self, other_path))

    def existence_of(self, *paths):
        return [self.existence_of_single(p) for p in paths]

    def existence_of_single(self, path):  # type: (MyPath) -> str
        path = self / path
        existence = os.path.exists(path)
        existence_message = {
            True: "exists",
            False: "does not exist"
        }[existence]
        return "%s: %s" % (path.replace(self, ''), existence_message)

    def mkdir_rel(self, path):
        RealFs().mkdir(self / path)

    def symlink_rel(self, src, dest):
        RealFs().symlink(self / src, self / dest)

    def list_dir_rel(self):
        return RealFs().listdir(self)

    @property
    def parent(self):  # type: (...) -> MyPath
        return MyPath(os.path.dirname(self))

    def clean_up(self):
        shutil.rmtree(self)

    @classmethod
    def make_temp_dir(cls):
        return cls(os.path.realpath(tempfile.mkdtemp(suffix="_trash_cli_test")))

    def list_all_files_sorted(self):
        return sorted([p.replace(self, '')
                       for p in list_all(RealFs(), self)])
