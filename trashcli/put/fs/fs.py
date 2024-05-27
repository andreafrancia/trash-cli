import os
from abc import abstractmethod
from typing import Iterable

from six import binary_type
from six import text_type
from trashcli.fs import PathExists

from trashcli.compat import Protocol
from trashcli.lib import TrashInfoContent


class RealPathFs(Protocol):
    @abstractmethod
    def realpath(self, path):
        raise NotImplementedError


class MakeFileFs(Protocol):
    @abstractmethod
    def make_file(self, path, content):
        raise NotImplementedError


class MakeDirsFs(Protocol):
    @abstractmethod
    def makedirs(self, path, mode):
        raise NotImplementedError


ModeNotSpecified = object()


class Fs(RealPathFs,
         MakeFileFs,
         MakeDirsFs,
         PathExists,
         Protocol):
    @abstractmethod
    def atomic_write(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def chmod(self, path, mode):
        raise NotImplementedError

    @abstractmethod
    def isdir(self, path):
        raise NotImplementedError

    @abstractmethod
    def isfile(self, path):
        raise NotImplementedError

    @abstractmethod
    def get_file_size(self, path):
        raise NotImplementedError

    @abstractmethod
    def makedirs(self, path, mode=ModeNotSpecified):
        raise NotImplementedError

    @abstractmethod
    def remove_file(self, path):
        raise NotImplementedError

    @abstractmethod
    def islink(self, path):
        raise NotImplementedError

    @abstractmethod
    def has_sticky_bit(self, path):
        raise NotImplementedError

    @abstractmethod
    def is_accessible(self, path):
        raise NotImplementedError

    @abstractmethod
    def read_file(self, path):  # type: (...) -> binary_type
        raise NotImplementedError

    def read_text(self, path,
                  ):  # type: (...) -> text_type
        return self.read_file(path).decode('utf-8')

    @abstractmethod
    def write_file(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def get_mod(self, path):
        raise NotImplementedError

    @abstractmethod
    def lexists(self, path):
        raise NotImplementedError

    @abstractmethod
    def walk_no_follow(self, top):
        raise NotImplementedError

    @abstractmethod
    def set_sticky_bit(self, path):
        raise NotImplementedError

    @abstractmethod
    def unset_sticky_bit(self, path):
        raise NotImplementedError

    def parent_realpath2(self, path):
        parent = os.path.dirname(path)
        return self.realpath(parent)

    def list_sorted(self, path):
        return sorted(self.listdir(path))

    def mkdir_p(self, path):
        if not self.isdir(path):
            self.makedirs(path)

    def make_file_p(self, path,
                    content,  # type: TrashInfoContent
                    ):  # type: (...) -> None
        self.mkdir_p(os.path.dirname(self.realpath(path)))
        self.make_file(path, content)

    def make_text_file(self,
                       path,
                       content,  # type: text_type
                       ):  # type: (...) -> None
        self.make_file(path, content.encode('utf-8'))

    def make_parent_for(self, path):
        parent = os.path.dirname(self.realpath(path))
        self.mkdir_p(parent)

    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        for entry in self.listdir(path):
            yield os.path.join(path, entry)

def list_all(fs, path):  # type: (Fs, str) -> Iterable[str]
    result = fs.walk_no_follow(path)
    for top, dirs, non_dirs in result:
        for d in dirs:
            yield os.path.join(top, d)
        for f in non_dirs:
            yield os.path.join(top, f)
