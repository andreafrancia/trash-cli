from typing import TypeVar

from tests.support.dirs.my_path import MyPath
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
