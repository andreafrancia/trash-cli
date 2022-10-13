import os

from tests.put.support.fake_fs.directory import Directory
from tests.put.support.fake_fs.inode import SymLink, INode
from tests.put.support.fake_fs.file import File
from tests.put.support.my_file_not_found_error import MyFileNotFoundError


class FakeFs:
    def __init__(self, cwd='/'):
        inode = INode(0o755, sticky=False)
        directory = Directory('/', inode, inode)
        inode.set_file_or_dir(directory)
        self.root = directory
        self.cwd = cwd

    def ls_aa(self, path):
        all_entries = self.ls_a(path)
        all_entries.remove(".")
        all_entries.remove("..")
        return all_entries

    def ls_a(self, path):
        dir = self.find_dir_or_file(path)
        return list(dir.entries())

    def mkdir(self, path):
        dirname, basename = os.path.split(path)
        dir = self.find_dir_or_file(dirname)
        dir.add_dir(basename, 0o755)

    def find_dir_or_file(self, path):  # type: (str) -> Directory or File
        path = os.path.join(self.cwd, path)
        if path == '/':
            return self.root
        cur_dir = self.root
        for component in self.components_for(path):
            try:
                cur_dir = cur_dir.get_file(component)
            except KeyError:
                raise MyFileNotFoundError(
                    "no such file or directory: %s" % path)
        return cur_dir

    def components_for(self, path):
        return path.split('/')[1:]

    def atomic_write(self, path, content):
        self.make_file(path, content)

    def read(self, path):
        return self.find_dir_or_file(path).content

    def make_file(self, path, content=''):
        path = os.path.join(self.cwd, path)
        dirname, basename = os.path.split(path)
        dir = self.find_dir_or_file(dirname)
        dir.add_file(basename, content)

    def get_mod(self, path):
        entry = self._find_entry(path)
        return entry.mode

    def _find_entry(self, path):
        path = os.path.join(self.cwd, path)
        dirname, basename = os.path.split(path)
        dir = self.find_dir_or_file(dirname)
        return dir._get_entry(basename)

    def chmod(self, path, mode):
        entry = self._find_entry(path)
        entry.chmod(mode)

    def isdir(self, path):
        try:
            file = self.find_dir_or_file(path)
        except MyFileNotFoundError:
            return False
        return isinstance(file, Directory)

    def exists(self, path):
        try:
            self.find_dir_or_file(path)
            return True
        except MyFileNotFoundError:
            return False

    def remove_file(self, path):
        dirname, basename = os.path.split(path)
        dir = self.find_dir_or_file(dirname)
        dir.remove(basename)

    def makedirs(self, path, mode):
        cur_dir = self.root
        for component in self.components_for(path):
            try:
                cur_dir = cur_dir.get_file(component)
            except KeyError:
                cur_dir.add_dir(component, mode)
                cur_dir = cur_dir.get_file(component)

    def move(self, src, dest):
        basename, entry = self._pop_entry_from_dir(src)

        if self.exists(dest) and self.isdir(dest):
            dest_dir = self.find_dir_or_file(dest)
            dest_dir._add_entry(basename, entry)
        else:
            dest_dirname, dest_basename = os.path.split(dest)
            dest_dir = self.find_dir_or_file(dest_dirname)
            dest_dir._add_entry(dest_basename, entry)

    def _pop_entry_from_dir(self, path):
        dirname, basename = os.path.split(path)
        dir = self.find_dir_or_file(dirname)
        entry = dir._get_entry(basename)
        dir.remove(basename)
        return basename, entry

    def islink(self, path):
        try:
            entry = self._find_entry(path)
        except MyFileNotFoundError:
            return False
        else:
            return isinstance(entry, SymLink)

    def symlink(self, src, dest):
        dest = os.path.join(self.cwd, dest)
        dirname, basename = os.path.split(dest)
        if dirname == '':
            raise OSError("only absolute dests are supported, got %s" % dest)
        dir = self.find_dir_or_file(dirname)
        dir.add_link(basename, src)

    def has_sticky_bit(self, path):
        return self._find_entry(path).sticky

    def set_sticky_bit(self, path):
        entry = self._find_entry(path)
        entry.sticky = True

    @staticmethod
    def realpath(path):
        return os.path.join("/", path)

    def cd(self, path):
        self.cwd = path

    def isfile(self, path):
        try:
            file = self.find_dir_or_file(path)
        except MyFileNotFoundError:
            return False
        return isinstance(file, File)

    def getsize(self, path):
        file = self.find_dir_or_file(path)
        return file.getsize()
