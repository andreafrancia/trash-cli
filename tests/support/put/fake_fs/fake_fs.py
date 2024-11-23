import errno
import os

from typing import cast

from six import binary_type

from tests.support.fakes.fake_volume_of import FakeVolumeOf
from tests.support.put.fake_fs.directory import Directory
from tests.support.put.fake_fs.directory import make_inode_dir
from tests.support.put.fake_fs.ent import Ent
from tests.support.put.fake_fs.entry import Entry
from tests.support.put.fake_fs.file import File
from tests.support.put.fake_fs.inode import INode
from tests.support.put.fake_fs.inode import Stickiness
from tests.support.put.fake_fs.symlink import SymLink
from tests.support.put.format_mode import format_mode
from tests.support.put.my_file_not_found_error import MyFileNotFoundError
from tests.support.restore.fs.fs_state import FsState
from trashcli.fs import MakeFileExecutable
from trashcli.fs import PathExists
from trashcli.put.check_cast import check_cast
from trashcli.put.fs.fs import Fs
from trashcli.put.fs.fs import ModeNotSpecified
from trashcli.put.fs.fs import list_all
from trashcli.put.fs.real_fs import Stat
from trashcli.put.fs.script_fs import ScriptFs


def as_directory(ent):  # type: (Ent) -> Directory
    return check_cast(Directory, ent)


def as_inode(entry):  # type: (Entry) -> INode
    return check_cast(INode, entry)

class FakeFs(FakeVolumeOf, Fs, PathExists, MakeFileExecutable, ScriptFs):
    def __init__(self, cwd='/'):
        super(FakeFs, self).__init__()
        self.root_inode = make_inode_dir('/', 0o755, None)
        self.root = self.root_inode.directory()
        self.cwd = cwd

    def touch(self, path):
        if not self.exists(path):
            self.make_file(path, b'')

    def ls_existing(self, paths):
        return [p for p in paths if self.exists(p)]

    def ls_aa(self, path):
        all_entries = self.ls_a(path)
        all_entries.remove(".")
        all_entries.remove("..")
        return all_entries

    def ls_a(self, path):
        directory = self.get_entity_at(path)
        return list(directory.entries())

    def mkdir(self, path):
        dirname, basename = os.path.split(path)
        directory = self.get_entity_at(dirname)
        directory.add_dir(basename, 0o755, path)

    def get_entity_at(self, path):  # type: (str) -> Ent
        inode = check_cast(INode, self.get_entry_at(path))
        return inode.entity

    def get_directory_at(self, path):
        return as_directory(self.get_entity_at(path))

    def get_entry_at(self, path):  # type: (str) -> Entry
        path = self._join_cwd(path)
        entry = self.root_inode
        for component in self.components_for(path):
            entry = as_inode(entry).directory().get_entry(component)
        return entry

    def makedirs(self, path, mode=ModeNotSpecified):
        mode = 0o777 if mode == ModeNotSpecified else mode
        path = self._join_cwd(path)
        inode = self.root_inode
        for component in self.components_for(path):
            try:
                inode = inode.directory().get_entry(component)
            except MyFileNotFoundError:
                directory = inode.directory()
                directory.add_dir(component, mode, path)
                inode = directory.get_entry(component)

    def _join_cwd(self, path):
        return os.path.join(os.path.join("/", self.cwd), path)

    def components_for(self, path):
        if path == '/':
            return []
        return path.split('/')[1:]

    def atomic_write(self, path,
                     content,  # type: binary_type
                     ):
        if self.exists(path):
            raise OSError("already exists: %s" % path)
        self.make_file(path, content)

    def listdir(self, path):
        directory = self.get_entry_at(path)
        if (directory.mode & 0o500) != 0o500:
            raise OSError(errno.EACCES,
                          "No permission to read: %s (%o)" % (path,
                                                              directory.mode))
        return self.sudo_listdir(path)

    def sudo_listdir(self, path):
        return self.ls_aa(path)

    def read_file(self, path):  # type: (...) -> binary_type
        path = self._join_cwd(path)
        dirname, basename = os.path.split(os.path.normpath(path))
        directory = as_directory(self.get_entity_at(dirname))
        entry = self.get_entry_at(path)
        if isinstance(entry, SymLink):
            link_target = self.readlink(path)
            return self.read_file(os.path.join(dirname, link_target))
        elif as_inode(entry).mode & 0o200 == 0:
            raise IOError("No permission to read: %s" % path)
        elif isinstance(as_inode(entry).entity, File):
            return cast(File, as_inode(entry).entity).content
        else:
            raise IOError("Unable to read: %s" % path)

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

    def make_file_and_dirs(self, path, content=b''):
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        self.makedirs(dirname, 0o755)
        self.make_file(path, content)

    def make_file(self, path,
                  content=b'',  # type: binary_type
                  ):  # type: (...) -> None
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        directory = self.get_entity_at(dirname)
        directory.add_file(basename, content, path)

    def write_file(self, path,
                   content,  # type: binary_type
                   ):  # type: (...) -> None
        if type(content) is not binary_type:
            raise ValueError("Content must be binary type: %s, %s" % (
                type(content), repr(content)))
        self.make_file(path, content)

    def get_mod(self, path):
        entry = self._find_entity(path)
        return entry.mode

    def _find_entity(self,
                     path
                     ): # type: (...) -> Entry
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        directory = self.get_entity_at(dirname)
        if not isinstance(directory, Directory):
            raise ValueError("Is not a directory: %s" % path)
        return directory.get_entry(basename)

    def lstat(self, path):
        inode = self._find_entity(path)
        return Stat(mode=inode.mode, uid="user-hard-coded", gid="git-hard-coded")

    def is_executable(self, path):
        return self.lstat(path).is_executable()

    def make_file_executable(self, path):
        self._find_entity(path).make_executable()

    def chmod(self, path, mode):
        entry = self._find_entity(path)
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
        directory = self.get_entity_at(dirname)
        directory.remove(basename)

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
        entry = directory.get_entry(basename)
        directory.remove(basename)
        return basename, entry

    def islink(self, path):
        try:
            entry = self._find_entity(path)
        except MyFileNotFoundError:
            return False
        else:
            return isinstance(entry, SymLink)

    def symlink(self, src, dest):
        dest = os.path.join(self.cwd, dest)
        dirname, basename = os.path.split(dest)
        if dirname == '':
            raise OSError("only absolute dests are supported, got %s" % dest)
        directory = as_directory(self.get_entity_at(dirname))
        directory.add_link(basename, src)

    def has_sticky_bit(self, path):
        return self._find_entity(path).stickiness is Stickiness.sticky

    def set_sticky_bit(self, path):
        entry = self._find_entity(path)
        entry.stickiness = Stickiness.sticky

    def unset_sticky_bit(self, path):
        entry = self._find_entity(path)
        entry.stickiness = Stickiness.not_sticky

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

    def get_file_size(self, path):
        file = self.get_entity_at(path)
        return file.getsize()

    def is_accessible(self, path):
        return self.exists(path)

    def get_mod_s(self, path):
        mode = self.get_mod(path)
        return format_mode(mode)

    def walk_no_follow(self, top):
        names = self.sudo_listdir(top)

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

    def read_all_files(self):
        return [(f, self.read_text(f))
                for f in list_all(self, "/")
                if self.isfile(f)]

    def find_all_sorted(self):
        return sorted(self.find_all())

    def save_state(self):
        return FsState(self.fs)
