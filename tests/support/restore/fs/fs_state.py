from enum import Enum

from six import binary_type
from six import text_type
from typing import List
from typing import NamedTuple
from typing import Optional

from tests.support.asserts import Unidiff
from tests.support.put.fake_fs.fake_fs import FakeFs


class EntryType(Enum):
    directory = "directory"
    file = "file"
    link = "link"


class Description(NamedTuple('EntryDescription', [
    ('path', text_type),
    ('entry_type', EntryType),
    ('content', Optional[binary_type]),
])):
    @staticmethod
    def description_for(fake_fs,  # type: FakeFs
                        path,  # type: text_type
                        ):
        if fake_fs.isdir(path):
            return Description(path, EntryType.directory, None)
        if fake_fs.isfile(path):
            return Description(path, EntryType.file, fake_fs.read_file(path))
    def for_human(self):
        def info():
            if self.entry_type == EntryType.directory:
                return "/"
            if self.entry_type == EntryType.link:
                return "@"
            if self.entry_type == EntryType.file:
                return ": %s" % binary_type(self.content).decode('utf-8')
        return self.path + info()

class FsState:
    def __init__(self, fake_fs):
        self.state = []
        self.fake_fs = fake_fs

        for path in fake_fs.find_all_sorted():
            self._add_path(path, fake_fs)

    def _add_path(self, path, fake_fs):
        self.state.append(Description.description_for(fake_fs, path))

    def __repr__(self):
        return "State(%s)" % repr(self.state)

    def describe_all(self):
        return [descr.for_human() for descr in self.state]

    def all_descriptions(self):
        return (description for description in self.state)

    def check_final_listing_is(self,
                               expected_listing,  # type: List[text_type]
                               ):
        actual_listing = FsState(self.fake_fs).describe_all()
        comparison = Unidiff(expected_listing, actual_listing)
        if not comparison.are_equals():
            return comparison.unidiff_as_list()
        else:
            return ''

    def check_file_removed(self, path):
        if not self._find_entry(path, EntryType.file):
            return ("File not removed because it didn't existed at the "
                    "beginning: %s" % path)
        if self.fake_fs.exists(path):
            return "File not removed because it still exists: %s" % path
        return ''

    def check_directory_created(self,
                                path,  # type: text_type
                                ):
        if self._directory_existed(path):
            return "already directory existed before: %s" % path
        if not self.fake_fs.isdir(path):
            return 'directory has not been created: %s' % path
        return ''

    def check_file_moved(self, src, dest):
        if not self._find_entry(src, EntryType.file):
            return 'File not moved because source file did not exists: %s' % src
        if not self.fake_fs.exists(dest):
            return 'File not moved because destination does not exists: %s' % dest
        if not self.fake_fs.isfile(dest):
            return 'File not moved because destination is not a file: %s' % dest
        source_content = self._find_description_of(src).content
        dest_content = self.fake_fs.read_file(dest)
        if source_content != dest_content:
            return (
                    'File not moved because destination contains a '
                    'different content, '
                    'dest: %s, '
                    'dest content: %s'
                    % (dest, dest_content)
            )
        return ''

    def _directory_existed(self,
                           path,  # type: text_type
                           ):
        if self._find_entry(path, EntryType.directory):
            return True
        return False

    def _find_description_of(self, path):
        for description in self.state:
            if description.path == path:
                return description
        raise DescriptionNotFound("path not found: %s" % path)

    def _find_entry(self,
                    path,  # type: text_type
                    entry_type,  # type: EntryType
                    ):
        try:
            description = self._find_description_of(path)
            return description.entry_type == entry_type
        except DescriptionNotFound:
            return False


class DescriptionNotFound(Exception):
    pass
