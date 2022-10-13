from collections import OrderedDict

from tests.put.support.fake_fs.inode import INode, SymLink
from tests.put.support.fake_fs.file import File
from tests.put.support.my_file_not_found_error import MyFileNotFoundError


class Directory:
    def __init__(self, name, inode, parent_inode):
        self.name = name
        self._entries = OrderedDict()
        self._entries['.'] = inode
        self._entries['..'] = parent_inode

    def entries(self):
        return self._entries.keys()

    def add_dir(self, basename, mode):
        inode = INode(mode, sticky=False)
        directory = Directory(basename, inode, self._inode())
        inode.set_file_or_dir(directory)
        self._entries[basename] = inode

    def _inode(self):  # type: ()->INode
        return self._entries["."]

    def get_file(self, basename):
        return self._entries[basename].file_or_dir

    def add_file(self, basename, content):
        inode = INode(0o644, sticky=False)
        file = File(content)
        inode.set_file_or_dir(file)
        self._entries[basename] = inode

    def _add_entry(self, basename, entry):
        self._entries[basename] = entry

    def add_link(self, basename, src):
        self._entries[basename] = SymLink(src)

    def _get_entry(self, basename):  # type: (str) -> INode
        try:
            return self._entries[basename]
        except KeyError:
            raise MyFileNotFoundError(
                "no such file or directory: %s" % basename)

    def remove(self, basename):
        self._entries.pop(basename)
