import os
from typing import TypeVar, Type

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
                  s,  # type: str
                  ):  # type: (...) -> str
        return s.replace(self, '')

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

    def rel_path(self,  # type: Self
                 path,  # type: str
                 ):  # type: (...) -> str
        if path.startswith(self):
            return path[len(self):]
        raise ValueError("path %s is not under %s" % (path, self))

    @property
    def parent(self,  # type: Self
               ):  # type: (...) -> MyPath
        return MyPath(os.path.dirname(self), self.fs)

    def clean_up(self,  # type: Self
                 ):
        self.fs.shutil_rmtree(self)

