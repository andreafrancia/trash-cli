import os
from typing import Union

from tests.test_put.support.fake_fs.directory import Directory
from tests.test_put.support.fake_fs.directory import make_inode_dir
from tests.test_put.support.fake_fs.file import File
from tests.test_put.support.fake_fs.symlink import SymLink
from tests.test_put.support.format_mode import format_mode
from tests.test_put.support.my_file_not_found_error import MyFileNotFoundError
from trashcli.fs import PathExists
from trashcli.put.fs.fs import Fs
from trashcli.put.fs.fs import list_all


class FakeFs(Fs, PathExists):
    def __init__(self, cwd='/'):
        self.root_inode = make_inode_dir('/', 0o755, None)
        self.root = self.root_inode.entity
        self.cwd = cwd

    def touch(self, path):
        if not self.exists(path):
            self.make_file(path, '')

    def listdir(self, path):
        return self.ls_aa(path)

    def ls_existing(self, paths):
        return [p for p in paths if self.exists(p)]

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
        dir.add_dir(basename, 0o755, path)

    def find_dir_or_file(self, path):  # type: (str) -> Union[Directory,File]
        path = self._join_cwd(path)
        inode = self.root_inode
        for component in self.components_for(path):
            try:
                inode = inode.entity.get_inode(component)
            except KeyError:
                raise MyFileNotFoundError(
                    "no such file or directory: %s\n%s" % (
                        path,
                        "\n".join(list_all(self, "/")),
                    ))
        return inode.entity

    def makedirs(self, path, mode):
        path = self._join_cwd(path)
        inode = self.root_inode
        for component in self.components_for(path):
            try:
                inode = inode.entity.get_inode(component)
            except KeyError:
                inode.entity.add_dir(component, mode, path)
                inode = inode.entity.get_inode(component)

    def _join_cwd(self, path):
        return os.path.join(os.path.join("/", self.cwd), path)

    def components_for(self, path):
        if path == '/':
            return []
        return path.split('/')[1:]

    def atomic_write(self, path, content):
        if self.exists(path):
            raise OSError("already exists: %s" % path)
        self.make_file(path, content)

    def read(self, path):
        return self.find_dir_or_file(path).content

    def read_null(self, path):
        try:
            return self.find_dir_or_file(path).content
        except MyFileNotFoundError:
            return None

    def make_file_and_dirs(self, path, content=''):
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        self.makedirs(dirname, 0o755)
        self.make_file(path, content)

    def make_file(self, path, content=''):
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        dir = self.find_dir_or_file(dirname)
        dir.add_file(basename, content, path)

    def get_mod(self, path):
        entry = self._find_entry(path)
        return entry.mode

    def _find_entry(self, path):
        path = self._join_cwd(path)
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

    def realpath(self, path):
        path = self._join_cwd(path)
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

    def is_accessible(self, path):
        return self.exists(path)

    def get_mod_s(self, path):
        mode = self.get_mod(path)
        return format_mode(mode)

    def walk_no_follow(self, top):
        names = self.listdir(top)

        dirs, nondirs = [], []
        for name in names:
            if self.isdir(os.path.join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)

        yield top, dirs, nondirs
        for name in dirs:
            new_path = os.path.join(top, name)
            if not self.islink(new_path):
                for x in self.walk_no_follow(new_path):
                    yield x

    def lexists(self, path):
        # TODO: consider links
        return self.exists(path)


