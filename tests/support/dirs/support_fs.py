from typing import Any, Generator, TypeVar

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.list_all import list_all
from trashcli.fslib.protocols.fs import Fs

Self = TypeVar('Self', bound='SupportFs')


class SupportFs(object):

    def __init__(self,  # type: Self
                 fs,  # type: Fs
                 base_dir,  # type: MyPath
                 ):
        self.fs = fs
        self.base_dir = base_dir

    def read(self,  # type: Self
             path):
        return self.fs.read_file(self.base_dir / path)

    def existence_of(self,  # type: Self
                     *paths):
        return [self.existence_of_single(p) for p in paths]

    def existence_of_single(self,  # type: Self
                            path,  # type: MyPath
                            ):  # type: (...) -> str
        path = self.base_dir / path
        existence = self.fs.path_exists(path)
        existence_message = {
            True: "exists",
            False: "does not exist"
        }[existence]
        return "%s: %s" % (path.replace(self.base_dir, ''), existence_message)

    def exists(self,  # type: Self
               path,  # type: str
               ):  # type: (...) -> bool
        full_path = self.base_dir.join_no_slash(path)
        return self.fs.path_exists(full_path)

    def find_all(self,  # type: Self
                 ):  # type: (...) -> Generator[MyPath, Any, None]
        for path in list_all(self.fs, self.base_dir):
            yield MyPath(path, self.fs)

    def is_file(self,  # type: Self
                path,  # type: str
                ):  # type: (...) -> bool
        return self.fs.isfile(self.base_dir / path)
