import errno
import os
from typing import Iterable

from tests.support.fakes.fake_volume_of import FakeVolumeOf
from tests.support.put.fake_fs.directory import Directory
from tests.support.put.fake_fs.directory import make_inode_dir
from tests.support.put.fake_fs.ent import Ent
from tests.support.put.fake_fs.file import File
from tests.support.put.fake_fs.inode import INode
from tests.support.put.fake_fs.inode import Stickiness
from tests.support.put.fake_fs.symlink import SymLink
from tests.support.put.format_mode import format_mode
from tests.support.put.my_file_not_found_error import MyFileNotFoundError
from trashcli.fslib.protocols.is_sticky_dir import IsStickyDir
from trashcli.fslib.protocols.is_sym_link import IsSymLink
from trashcli.put.check_cast import check_cast
from trashcli.fslib.protocols.dir_reader_fs import DirReaderFs
from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.protocols.remove_file_if_exists import RemoveFileIfExists
from trashcli.fslib.list_all import list_all
from trashcli.restore.fs.protocols.restore_fs import RestoreFs


def as_directory(ent):  # type: (Ent) -> Directory
    return check_cast(Directory, ent)


MAX_SYMLINKS_TO_FOLLOW = 40


class FakeFs(FakeVolumeOf, Fs, DirReaderFs, IsStickyDir, IsSymLink, RestoreFs,
             RemoveFileIfExists):
    def __init__(self, cwd='/'):
        super(FakeFs, self).__init__()
        self.root_inode = make_inode_dir('/', 0o755, None)
        self.root = self.root_inode.directory()
        self.cwd = cwd
        self._finding_all = False

    def touch(self, path):
        if not self.path_exists(path):
            self.write_file(path, '')

    def listdir(self, path):
        return self.ls_aa(path)

    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        for entry in self.listdir(path):
            yield os.path.join(path, entry)

    def mkdirs(self, path):  # type: (str) -> None
        self.makedirs(path, 0o755)

    def getcwd_as_realpath(self):  # type: () -> str
        return os.path.join('/', self.cwd)

    def list_mount_points(self):
        return self.volumes

    def ls_existing(self, paths):
        return [p for p in paths if self.path_exists(p)]

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
        return self._lookup(path, follow_last_link=True).entity

    def _get_directory_at(self, path):
        return as_directory(self.get_entity_at(path))

    def _get_entry_at(self, path):  # type: (str) -> INode
        return self._lookup(path, follow_last_link=False)

    def _lookup(self,
                path,  # type: str
                follow_last_link,  # type: bool
                ):  # type: (...) -> INode
        """Finds the INode that path refers to, walking down from the root.

        This is the path resolution of the fake file system, the counterpart
        of what the kernel does for stat() and lstat().

        Symbolic links met in the intermediate components are always
        followed. The last component is followed only if follow_last_link is
        True (stat() semantic: exists, isdir, isfile, read, ...); otherwise
        the INode of the link itself is returned (lstat() semantic: islink,
        lexists, readlink, remove_file, ...).

        To follow a link the path is rewritten, replacing the components up to
        and including the link with its target (resolved against the link's
        directory if relative), and the walk restarts from the root. After
        MAX_SYMLINKS_TO_FOLLOW rewrites (e.g. a link pointing to itself) it
        gives up, like ELOOP.

        Raises MyFileNotFoundError if a component does not exist, which
        includes a dangling link that has to be followed.
        """
        path = self._join_cwd(path)
        for _ in range(MAX_SYMLINKS_TO_FOLLOW):
            components = self._components_for(path)
            inode = self.root_inode
            for index, component in enumerate(components):
                inode = inode.directory().get_entry(component, path, self)
                is_last = index == len(components) - 1
                if isinstance(inode.entity, SymLink) and (
                        follow_last_link or not is_last):
                    parent = '/' + '/'.join(components[:index])
                    rest = components[index + 1:]
                    path = os.path.normpath(
                        os.path.join(parent, inode.entity.dest, *rest))
                    break
            else:
                return inode
        raise MyFileNotFoundError("too many levels of symbolic links: %s" % path)

    def makedirs(self, path, mode):
        path = self._join_cwd(path)
        inode = self.root_inode
        for component in self._components_for(path):
            try:
                inode = inode.directory().get_entry(component, path, self)
            except MyFileNotFoundError:
                directory = inode.directory()
                directory.add_dir(component, mode, path)
                inode = directory.get_entry(component, path, self)

    def _join_cwd(self, path):
        return os.path.join(os.path.join("/", self.cwd), path)

    def _components_for(self, path):
        if path == '/':
            return []
        return path.split('/')[1:]

    def atomic_write(self, path, content):
        if self.path_exists(path):
            raise OSError("already exists: %s" % path)
        self.write_file(path, content)

    def read_file(self,
                  path,  # type: str
                  ):  # type: (...) -> str
        path = self._join_cwd(path)
        entity = self.get_entity_at(os.path.normpath(path))
        if isinstance(entity, File):
            content = entity.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return content
        raise IOError("Unable to read: %s" % path)

    def readlink(self, path):
        path = self._join_cwd(path)
        entity = self._get_entry_at(path).entity
        if isinstance(entity, SymLink):
            return entity.dest
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
        self.write_file(path, content)

    def write_file(self,
                   path,  # type: str
                   content='',  # type: str
                   ):
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        directory = self._get_directory_at(dirname)
        directory.add_file(basename, content, path)

    def get_mod(self, path):
        entry = self._find_entry(path)
        return entry.mode

    def _find_entry(self, path):
        path = self._join_cwd(path)
        dirname, basename = os.path.split(path)
        directory = self.get_entity_at(dirname)
        return directory.get_entry(basename, path, self)

    def chmod(self, path, mode):
        entry = self._find_entry(path)
        entry.chmod(mode)

    def path_isdir(self, path):
        try:
            entity = self.get_entity_at(path)
        except MyFileNotFoundError:
            return False
        return isinstance(entity, Directory)

    def path_exists(self, path):
        try:
            self.get_entity_at(path)
            return True
        except MyFileNotFoundError:
            return False

    def remove_file(self, path):
        dirname, basename = os.path.split(path)
        directory = self.get_entity_at(dirname)
        directory.remove(basename)

    def remove_file2(self, path):
        self.remove_file(path)

    def remove_file_if_exists(self, path):
        if self.path_lexists(path):
            self.remove_file(path)

    def entries_if_dir_exists(self, path):  # type: (str) -> Iterable[str]
        if self.path_exists(path):
            for entry in self.listdir(path):
                yield entry

    def move(self, src, dest):
        basename, entry = self._pop_entry_from_dir(src)

        if self.path_exists(dest) and self.path_isdir(dest):
            dest_dir = self._get_directory_at(dest)
            dest_dir.add_entry(basename, entry)
        else:
            dest_dirname, dest_basename = os.path.split(dest)
            dest_dir = self._get_directory_at(dest_dirname)
            dest_dir.add_entry(dest_basename, entry)

    def _pop_entry_from_dir(self, path):
        dirname, basename = os.path.split(path)
        directory = self._get_directory_at(dirname)
        entry = directory.get_entry(basename, path, self)
        directory.remove(basename)
        return basename, entry

    def is_symlink(self, path):
        try:
            entry = self._find_entry(path)
        except MyFileNotFoundError:
            return False
        else:
            return isinstance(entry.entity, SymLink)

    def symlink(self, src, dest):
        dest = os.path.join(self.cwd, dest)
        dirname, basename = os.path.split(dest)
        if dirname == '':
            raise OSError("only absolute dests are supported, got %s" % dest)
        directory = as_directory(self.get_entity_at(dirname))
        directory.add_link(basename, src)

    def has_sticky_bit(self, path):
        # like os.stat(), it follows symlinks
        inode = self._lookup(path, follow_last_link=True)
        return inode.stickiness is Stickiness.sticky

    def set_sticky_bit(self, path):
        # like os.chmod(), it follows symlinks
        inode = self._lookup(path, follow_last_link=True)
        inode.stickiness = Stickiness.sticky

    def is_sticky_dir(self, path):  # type: (str) -> bool
        return self.path_isdir(path) and self.has_sticky_bit(path)

    def is_world_writable(self, path):  # type: (str) -> bool
        # like os.stat(), it follows symlinks: the mode of the link itself
        # (always 0o777) is not the one that matters
        try:
            return bool(self._lookup(path, follow_last_link=True).mode & 0o002)
        except MyFileNotFoundError:
            return False

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

    def file_size(self, path):
        file = self.get_entity_at(path)
        return file.getsize()

    def is_accessible(self, path):
        return self.path_exists(path)

    def seems_to_have_delete_permissions(self, path):
        parent = os.path.dirname(self._join_cwd(path))
        mode = self.root_inode.mode if parent == '/' else self.get_mod(parent)
        return bool(mode & 0o200)

    def get_mod_s(self, path):
        mode = self.get_mod(path)
        return format_mode(mode)

    def walk_no_follow(self, top):
        names = self.listdir(top)

        dirs, nondirs = [], []
        for name in names:
            if self.path_isdir(os.path.join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)

        yield top, dirs, nondirs
        for name in dirs:
            new_path = os.path.join(top, name)
            if not self.is_symlink(new_path):
                for x in self.walk_no_follow(new_path):
                    yield x

    def path_lexists(self, path):
        path = self._join_cwd(path)
        try:
            self._get_entry_at(path)
        except MyFileNotFoundError:
            return False
        else:
            return True

    def find_all(self):
        """Lists the paths of everything in the fake file system.

        It is used by the tests and also by Directory.get_entry() to put the
        whole content of the fs in the message of MyFileNotFoundError, to ease
        debugging.

        That makes it re-entrant: walking the fs calls isdir() on every entry
        and, with a dangling symlink (or a loop of symlinks), isdir() does a
        lookup that fails. Building the message of that failure calls
        find_all() again, which walks the fs again, meets the same symlink,
        and so on until RecursionError.

        _finding_all is the guard against that: while a find_all() is running,
        the nested calls (the ones made to build an error message) return []
        instead of walking again. The error is raised all the same, isdir()
        catches it and returns False, and the outer walk goes on; the only
        difference is that such a message does not list the fs.
        The flag is reset in a finally, so a failing walk does not leave the
        guard on.
        """
        if self._finding_all:
            return []
        self._finding_all = True
        try:
            return list(list_all(self, "/"))
        finally:
            self._finding_all = False
