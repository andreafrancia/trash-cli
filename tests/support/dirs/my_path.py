import os
from typing import TypeVar, Type

from six import StringIO

from trashcli.fslib.list_all import list_all
from trashcli.fslib.protocols.fs import Fs

Self = TypeVar('Self', bound='MyPath')


class MyPath(str):

    def __new__(cls,  # type: Type[Self]
                value,  # type: str
                fs,  # type: Fs
                ):  # type: (...) -> Self
        return super(MyPath, cls).__new__(cls, value)

    def __init__(self,  # type: Self
                 value,  # type: str
                 fs,  # type: Fs
                 ):
        super(MyPath, self).__init__()
        self.fs = fs

    def __truediv__(self,  # type: Self
                    other_path,
                    ):  # type: (...) -> MyPath
        return self.path_join(other_path)

    def clean_str(self,  # type: Self
                  stdout,  # type: StringIO
                  ):  # type: (...) -> str
        return stdout.getvalue().replace(self, '')

    def __div__(self,  # type: Self
                other_path):
        return self.path_join(other_path)

    def path_join(self,  # type: Self
                  other_path):
        return MyPath(os.path.join(self, other_path), self.fs)

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
        # Local import: tests.support.dirs.support_fs imports MyPath, so a
        # module-level import here would be circular. Transitional only,
        # until find_files_rel itself moves to SupportFs.
        from tests.support.dirs.support_fs import SupportFs
        support_fs = SupportFs(self.fs, self)
        for path in support_fs.find_all():
            if support_fs.is_file(path):
                yield self.rel_path(path)

    def rel_path(self,  # type: Self
                 path,  # type: str
                 ):  # type: (...) -> str
        if path.startswith(self):
            return path[len(self):]
        raise ValueError("path %s is not under %s" % (path, self))

    def is_dir(
            self,  # type: Self
    ):  # type: (...) -> bool
        return self.fs.path_isdir(self)

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

    def mkdir_rel_p(self,  # type: Self
                    path,
                    ):
        self.fs.mkdirs(self / path)

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
        return MyPath(os.path.dirname(self), self.fs)

    def clean_up(self,  # type: Self
                 ):
        self.fs.shutil_rmtree(self)

    def list_all_files_sorted(self,  # type: Self
                              ):
        return sorted([p.replace(self, '')
                       for p in list_all(self.fs, self)])
