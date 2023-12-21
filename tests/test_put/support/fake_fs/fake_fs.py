import errno
import os
from typing import Any
from typing import Type
from typing import TypeVar
from typing import cast

from tests.test_put.support.fake_fs.directory import Directory
from tests.test_put.support.fake_fs.directory import make_inode_dir
from tests.test_put.support.fake_fs.ent import Ent
from tests.test_put.support.fake_fs.entry import Entry
from tests.test_put.support.fake_fs.file import File
from tests.test_put.support.fake_fs.inode import INode
from tests.test_put.support.fake_fs.inode import Stickiness
from tests.test_put.support.fake_fs.symlink import SymLink
from tests.test_put.support.format_mode import format_mode
from tests.test_put.support.my_file_not_found_error import MyFileNotFoundError
from trashcli.fs import PathExists
from trashcli.put.fs.fs import Fs
from trashcli.put.fs.fs import list_all

T = TypeVar('T')


def check_cast(t, value):  # type: (Type[T], Any) -> T
    if isinstance(value, t):
        return cast(t, value)
    else:
        raise TypeError("expected %s, got %s" % (t, type(value)))


def as_directory(ent):  # type: (Ent) -> Directory
    return check_cast(Directory, ent)


def as_inode(entry):  # type: (Entry) -> INode
    return check_cast(INode, entry)


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
        dir = self.get_entity_at(path)
        return list(dir.entries())

    def mkdir(self, path):
        dirname, basename = os.path.split(path)
        dir = self.get_entity_at(dirname)
        dir.add_dir(basename, 0o755, path)

    def get_entity_at(self, path):  # type: (str) -> Ent
        return self.get_entry_at(path).entity

    def get_directory_at(self, path):
        return as_directory(self.get_entity_at(path))

    def get_entry_at(self, path):  # type: (str) -> Entry
        path = self._join_cwd(path)
        entry = self.root_inode
        for component in self.components_for(path):
            entry = as_directory(as_inode(entry).entity).get_inode(component, path, self)
        return entry

    def makedirs(self, path, mode):
        path = self._join_cwd(path)
        inode = self.root_inode
        for component in self.components_for(path):
            try:
                inode = inode.entity.get_inode(component, path, self)
            except FileNotFoundError:
                dir_ent = as_directory(inode.entity)
                inode.entity.add_dir(component, mode, path)
                inode = dir_ent.get_inode(component, path, self)

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
        path = self._join_cwd(path)
        dirname, basename = os.path.split(os.path.normpath(path))
        dir_ent = as_directory(self.get_entity_at(dirname))
        inode = dir_ent.get_inode(basename, path, self)
        if isinstance(inode, SymLink):
            link_target = self.readlink(path)
            return self.read(os.path.join(dirname, link_target))
        else:
            return inode.entity.content

    def readlink(self, path):
        path = self._join_cwd(path)
        maybe_link = self.get_entry_at(path)
        if isinstance(maybe_link, SymLink):
            return maybe_link.dest
        else:
            raise OSError(errno.EINVAL, "Invalid argument", path)

    def read_null(self, path):
        try:
            return self.get_entity_at(path).content
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
        dir = self.get_entity_at(dirname)
        dir.add_file(basename, content, path)

    def get_mod(self, path):
        entry = self._find_entry(path)
        return entry.mode

    def _find_entry(self, path):
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        dir_ent = self.get_entity_at(dirname)
        return dir_ent.get_inode(basename, path, self)

    def chmod(self, path, mode):
        entry = self._find_entry(path)
        entry.chmod(mode)

    def isdir(self, path):
        try:
            entry = self.get_entry_at(path)
        except MyFileNotFoundError:
            return False
        else:
            if isinstance(entry, SymLink):
                return False
            file = entry.entity
            return isinstance(file, Directory)

    def exists(self, path):
        try:
            self.get_entity_at(path)
            return True
        except MyFileNotFoundError:
            return False

    def remove_file(self, path):
        dirname, basename = os.path.split(path)
        dir = self.get_entity_at(dirname)
        dir.remove(basename)

    def move(self, src, dest):
        basename, entry = self._pop_entry_from_dir(src)

        if self.exists(dest) and self.isdir(dest):
            dest_dir = self.get_directory_at(dest)
            dest_dir.add_entry(basename, entry)
        else:
            dest_dirname, dest_basename = os.path.split(dest)
            dest_dir = self.get_directory_at(dest_dirname)
            dest_dir.add_entry(dest_basename, entry)

    def _pop_entry_from_dir(self, path):
        dirname, basename = os.path.split(path)
        directory = self.get_directory_at(dirname)
        entry = directory.get_inode(basename, path, self)
        directory.remove(basename)
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
        dir_ent = as_directory(self.get_entity_at(dirname))
        dir_ent.add_link(basename, src)

    def has_sticky_bit(self, path):
        return self._find_entry(path).stickiness is Stickiness.sticky

    def set_sticky_bit(self, path):
        entry = self._find_entry(path)
        entry.stickiness = Stickiness.sticky

    def realpath(self, path):
        path = self._join_cwd(path)
        return os.path.join("/", path)

    def cd(self, path):
        self.cwd = path

    def isfile(self, path):
        try:
            file = self.get_entity_at(path)
        except MyFileNotFoundError:
            return False
        return isinstance(file, File)

    def getsize(self, path):
        file = self.get_entity_at(path)
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
        path = self._join_cwd(path)
        try:
            self.get_entry_at(path)
        except MyFileNotFoundError:
            return False
        else:
            return True

    def find_all(self):
        return list(list_all(self, "/"))
