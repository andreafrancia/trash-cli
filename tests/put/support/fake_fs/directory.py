from collections import OrderedDict

from tests.put.support.fake_fs.entry import Entry
from tests.put.support.fake_fs.file import File


class Directory:
    def __init__(self, name, parent_dir=None):
        self.name = name
        parent_dir = parent_dir or self
        self._entries = OrderedDict()
        self._entries['.'] = self
        self._entries['..'] = parent_dir

    def entries(self):
        return self._entries.keys()

    def add_dir(self, basename):
        self._entries[basename] = Entry(Directory(basename, self), 0o755)

    def get_file(self, basename):
        return self._entries[basename].file

    def add_file(self, basename, content):
        self._entries[basename] = Entry(File(content), 0o644)

    def get_entry(self, basename):  # type: (str) -> Entry
        return self._entries[basename]

    def remove(self, basename):
        self._entries.pop(basename)
