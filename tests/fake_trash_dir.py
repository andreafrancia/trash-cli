import datetime
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
        make_file(trashinfo_path, trashinfo_content_default_date(path))
        make_file(file_path, content)

    def a_trashinfo(self, basename):
        return '%s/%s.trashinfo' % (self.info_path, basename)

    def file_path(self, basename):
        return '%s/%s' % (self.files_path, basename)

    def add_trashinfo2(self, path, deletion_date):
        basename = str(uuid.uuid4())
        self.add_trashinfo3(basename, path, deletion_date)

    def add_trashinfo3(self, basename, path, deletion_date):
        content = trashinfo_content(path, deletion_date)
        self.add_trashinfo_content(basename, content)

    def add_trashinfo_content(self, basename, content):
        trashinfo_path = '%(info_dir)s/%(name)s.trashinfo' % {'info_dir': self.info_path,
                                                              'name': basename}
        make_parent_for(trashinfo_path)
        make_file(trashinfo_path, content)

    def add_trashinfo(self,
                      path="foo",
                      formatted_deletion_date=None,
                      content=None,
                      basename=None):
        content = content if (content!=None) else a_trashinfo(path, formatted_deletion_date)
        basename = basename or str(uuid.uuid4())
        trashinfo_path = '%(info_dir)s/%(name)s.trashinfo' % {'info_dir': self.info_path,
                                                              'name': basename}
        make_parent_for(trashinfo_path)
        make_file(trashinfo_path, content)

    def ls_info(self):
        return os.listdir(self.info_path)


def a_trashinfo(path, formatted_deletion_date):
    return ("[Trash Info]\n" +
            ("Path=%s\n" % format_original_location(path) if path else '') +
            ("DeletionDate=%s\n" % formatted_deletion_date if formatted_deletion_date else ''))


def trashinfo_content_default_date(path):
    return trashinfo_content(path, datetime.datetime(2000,1,1,0,0,1))


def trashinfo_content(path, deletion_date):
    return ("[Trash Info]\n" +
            ("Path=%s\n" % format_original_location(path) if path else '') +
            ("DeletionDate=%s\n" % deletion_date.strftime('%Y-%m-%dT%H:%M:%S') if deletion_date else ''))
