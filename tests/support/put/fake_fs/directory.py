from collections import OrderedDict
from typing import Optional
from typing import Union

from tests.support.put.fake_fs.ent import Ent
from tests.support.put.fake_fs.inode import INode
from tests.support.put.fake_fs.inode import Stickiness
from tests.support.put.fake_fs.symlink import SymLink
from tests.support.put.fake_fs.file import File
from tests.support.put.my_file_not_found_error import MyFileNotFoundError
from trashcli.lib.my_permission_error import MyPermissionError


def make_inode_dir(directory_path,  # type: str
                   mode,  # type: int
                   parent_inode,  # type: Optional[INode]
                   ):  # type: (...)->INode
    directory = Directory(directory_path)
    inode = INode(directory, mode, Stickiness.not_sticky)
    directory.set_dot_entries(inode, parent_inode or inode)
    return inode


class Directory(Ent):
    def __init__(self, name):  # type: (str) -> None
        self.name = name
        self._entries = OrderedDict()  # type: dict[str, Union[INode, SymLink]]

    def __repr__(self):
        return "Directory(%r)" % self.name

    def set_dot_entries(self, inode, parent_inode):
        self._entries['.'] = inode
        self._entries['..'] = parent_inode

    def entries(self):
        return self._entries.keys()

    def add_dir(self, basename, mode, complete_path):
        if self._inode().mode & 0o200 == 0:
            raise MyPermissionError(
                "[Errno 13] Permission denied: '%s'" % complete_path)
        inode = make_inode_dir(basename, mode, self._inode())
        self._entries[basename] = inode

    def add_file(self, basename, content, complete_path):
        mode = 0o644
        if self._inode().mode & 0o200 == 0:
            raise MyPermissionError(
                "[Errno 13] Permission denied: '%s'" % complete_path)
        file = File(content)
        inode = INode(file, mode, Stickiness.not_sticky)
        self._entries[basename] = inode

    def _inode(self):  # type: ()->Union[INode, SymLink]
        return self._entries["."]

    def get_file(self, basename):
        return self._entries[basename].entity

    def get_entry(self, basename, path, fs):
        try:
            return self._entries[basename]
        except KeyError:
            raise MyFileNotFoundError(
                "no such file or directory: %s\n%s" % (
                    path,
                    "\n".join(fs.find_all()),
                ))

    def add_entry(self, basename, entry):
        self._entries[basename] = entry

    def add_link(self, basename, src):
        self._entries[basename] = SymLink(src)

    def remove(self, basename):
        self._entries.pop(basename)

    def getsize(self):
        raise NotImplementedError
