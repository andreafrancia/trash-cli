import os
import shutil
import stat
from abc import abstractmethod, ABCMeta
from typing import Iterable

import six


@six.add_metaclass(ABCMeta)
class PathExists:
    @abstractmethod
    def exists(self, path):
        raise NotImplementedError()


class FsMethods(PathExists):
    def entries_if_dir_exists(self, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                yield entry

    def exists(self, path):
        return os.path.exists(path)

    def is_sticky_dir(self, path):  # type: (str) -> bool
        import os
        return os.path.isdir(path) and self.has_sticky_bit(path)

    def is_symlink(self, path):  # type: (str) -> bool
        return os.path.islink(path)

    def contents_of(self, path):
        return self.read_file(path)

    def has_sticky_bit(self, path):
        import os
        import stat
        return (os.stat(path).st_mode & stat.S_ISVTX) == stat.S_ISVTX

    def remove_file(self, path):
        if (os.path.lexists(path)):
            try:
                os.remove(path)
            except:
                return shutil.rmtree(path)

    def remove_file2(self, path):
        try:
            os.remove(path)
        except OSError:
            shutil.rmtree(path)

    def remove_file_if_exists(self, path):
        if os.path.lexists(path): self.remove_file2(path)

    def move(self, path, dest):
        return shutil.move(path, str(dest))

    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        for entry in os.listdir(path):
            result = os.path.join(path, entry)
            yield result

    def mkdirs(self, path):
        if os.path.isdir(path):
            return
        os.makedirs(path)

    def atomic_write(self, path, content):
        file_handle = self.open_for_write_in_exclusive_and_create_mode(path)
        os.write(file_handle, content)
        os.close(file_handle)

    def open_for_write_in_exclusive_and_create_mode(self, path):
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)

    def read_file(self, path):
        with open(path) as f:
            return f.read()

    def write_file(self, name, contents):
        with open(name, 'w') as f:
            f.write(contents)

    def make_file_executable(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)

    def file_size(self, path):
        return os.stat(path).st_size


has_sticky_bit = FsMethods().has_sticky_bit
contents_of = FsMethods().contents_of
remove_file = FsMethods().remove_file
move = FsMethods().move
list_files_in_dir = FsMethods().list_files_in_dir
mkdirs = FsMethods().mkdirs
atomic_write = FsMethods().atomic_write
open_for_write_in_exclusive_and_create_mode = FsMethods().open_for_write_in_exclusive_and_create_mode
read_file = FsMethods().read_file
write_file = FsMethods().write_file
make_file_executable = FsMethods().make_file_executable
file_size = FsMethods().file_size
remove_file2 = FsMethods().remove_file2
