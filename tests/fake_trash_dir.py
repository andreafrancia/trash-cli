import os
import uuid

from trashcli.put import format_original_location
from .files import make_parent_for, make_file, make_unreadable_file


class FakeTrashDir:
    def __init__(self, path):
        self.info_path = os.path.join(path, 'info')
        self.files_path = os.path.join(path, 'files')

    def add_unreadable_trashinfo(self, basename):
        path = self.a_trashinfo(basename)
        make_unreadable_file(path)

    def add_trashed_file(self, basename, path, content):
        trashinfo_path = self.a_trashinfo(basename)
        file_path = self.file_path(basename)
        make_file(trashinfo_path, a_trashinfo(path))
        make_file(file_path, content)

    def a_trashinfo(self, basename):
        return '%s/%s.trashinfo' % (self.info_path, basename)

    def file_path(self, basename):
        return '%s/%s' % (self.files_path, basename)

    def add_trashinfo(self,
                      path="foo",
                      formatted_deletion_date=None,
                      contents=None,
                      basename=None):
        contents = contents if (contents!=None) else a_trashinfo(path, formatted_deletion_date)
        basename = basename or str(uuid.uuid4())
        trashinfo_path = '%(info_dir)s/%(name)s.trashinfo' % {'info_dir': self.info_path,
                                                              'name': basename}
        make_parent_for(trashinfo_path)
        make_file(trashinfo_path, contents)

    def ls_info(self):
        return os.listdir(self.info_path)

def a_trashinfo(path,
                formatted_deletion_date='2000-01-01T00:00:01'):
    return ("[Trash Info]\n" +
            ("Path=%s\n" % format_original_location(path) if path else '') +
            ("DeletionDate=%s\n" % formatted_deletion_date if formatted_deletion_date else ''))
