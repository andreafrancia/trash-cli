import os
import shutil
import tempfile
from typing import Any, Generator, TypeVar

from six import StringIO

from trashcli.put.fs.fs import list_all
from trashcli.put.fs.real_fs import RealFs

Self = TypeVar('Self', bound='MyPath')


class MyPath(str):

    def __init__(self,  # type: Self
                 *args, **kwargs):
        super(MyPath, self).__init__()
        self.fs = RealFs()

    def __truediv__(self,  # type: Self
                    other_path,
                    ):  # type: (...) -> MyPath
        return self.path_join(other_path)

    def clean_str(self,  # type: Self
                  stdout,  # type: StringIO
                  ):  # type: (...) -> str
        return stdout.getvalue().replace(self, '')

    def read(self,  # type: Self
             path):
        return self.fs.read(self / path)

    def __div__(self,  # type: Self
                other_path):
        return self.path_join(other_path)

    def path_join(self,  # type: Self
                  other_path):
        return MyPath(os.path.join(self, other_path))

    def existence_of(self,  # type: Self
                     *paths):
        return [self.existence_of_single(p) for p in paths]

    def existence_of_single(self,  # type: Self
                            path,  # type: MyPath
                            ):  # type: (...) -> str
        path = self / path
        existence = os.path.exists(path)
        existence_message = {
            True: "exists",
            False: "does not exist"
        }[existence]
        return "%s: %s" % (path.replace(self, ''), existence_message)

    def exists(self,  # type: Self
               path,  # type: str
               ):  # type: (...) -> bool
        full_path = self.join_no_slash(path)
        return os.path.exists(full_path)

    def join_no_slash(self,  # type: Self
                      path,  # type: str
                      ):
        no_slash = self._no_slash(path)
        return self / no_slash

    @staticmethod
    def _no_slash(path):
        while path.startswith('/'):
            path = path[1:]
        return path

    def find_files_rel(self,  # type: Self
                       ):
        for path in self.find_all():
            if path.is_file():
                yield self.rel_path(path)

    def find_all(self,  # type: Self
                 ):  # type: (...) -> Generator[MyPath, Any, None]
        for path in list_all(self.fs, self):
            yield MyPath(path)

    def rel_path(self,  # type: Self
                 path,  # type: str
                 ):  # type: (...) -> str
        if path.startswith(self):
            return path[len(self):]
        raise ValueError("path %s is not under %s" % (path, self))

    def is_file(self,  # type: Self
                ):  # type: (...) -> bool
        return self.fs.isfile(self)

    def is_dir(
            self,  # type: Self
    ):  # type: (...) -> bool
        return self.fs.isdir(self)

    def touch(self,  # type: Self
              path):
        self.fs.touch(self / path)

    def write_file(self,  # type: Self
                   path, content):
        self.fs.write_file(self / path, content)

    def symlink_rel(self,  # type: Self
                    src, dest):
        self.fs.symlink(self / src, self / dest)

    def mkdir_rel(self,  # type: Self
                  path,
                  ):
        self.fs.mkdir(self / path)
        return self / path

    def mkdir_rel_p(self,  # type: Self
                    path,
                    ):
        self.fs.mkdirs(self / path)
        return self / path

    def mkdirs(self,  # type: Self
               ):
        self.fs.mkdirs(self)
        return self

    def list_dir_rel(self,  # type: Self
                     ):
        return self.fs.listdir(self)

    @property
    def parent(self,  # type: Self
               ):  # type: (...) -> MyPath
        return MyPath(os.path.dirname(self))

    def clean_up(self,  # type: Self
                 ):
        shutil.rmtree(self)

    @classmethod
    def make_temp_dir(
            cls
    ):  # type: (...) -> Self
        temp_from_os = tempfile.mkdtemp(suffix="_trash_cli_test")
        realpath_just_to_be_sure = os.path.realpath(temp_from_os)
        return cls(realpath_just_to_be_sure)

    def list_all_files_sorted(self,  # type: Self
                              ):
        return sorted([p.replace(self, '')
                       for p in list_all(RealFs(), self)])
