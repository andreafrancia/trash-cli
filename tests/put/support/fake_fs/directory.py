from collections import OrderedDict

from tests.put.support.fake_fs.inode import INode, SymLink
from tests.put.support.fake_fs.file import File
from tests.put.support.my_file_not_found_error import MyFileNotFoundError


class Directory:
    def __init__(self, name, parent_dir=None):
        self.name = name
        parent_dir = parent_dir or self
        self._entries = OrderedDict()
        self._entries['.'] = self
        self._entries['..'] = parent_dir

    def entries(self):
        return self._entries.keys()

    def add_dir(self, basename, mode):
        self._entries[basename] = INode(Directory(basename, self), mode, False)

    def get_file(self, basename):
        return self._entries[basename].file_or_dir

    def add_file(self, basename, content):
        self._entries[basename] = INode(File(content), 0o644, False)

    def _add_entry(self, basename, entry):
        self._entries[basename] = entry

    def add_link(self, basename, src):
        self._entries[basename] = SymLink(src)

    def _get_entry(self, basename):  # type: (str) -> INode
        try:
            return self._entries[basename]
        except KeyError:
            raise MyFileNotFoundError("no such file or directory: %s" % basename)

    def remove(self, basename):
        self._entries.pop(basename)
