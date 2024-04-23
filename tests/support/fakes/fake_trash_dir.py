import datetime
import os
import uuid

from tests.support.files import does_not_exist
from tests.support.files import is_a_symlink_to_a_dir
from tests.support.files import make_sticky_dir
from tests.support.files import make_unsticky_dir
from trashcli.put.format_trash_info import format_original_location

from tests.support.files import make_file, make_parent_for, make_unreadable_file
from tests.support.trashinfo.parse_date import parse_date


def a_default_datetime():
    return datetime.datetime(2000, 1, 1, 0, 0, 1)


class FakeTrashDir:
    def __init__(self, path):
        self.path = path
        self.info_path = os.path.join(path, 'info')
        self.files_path = os.path.join(path, 'files')

    def add_unreadable_trashinfo(self, basename):
        path = self.a_trashinfo_path(basename)
        make_unreadable_file(path)

    def add_trashed_file(self, basename, path, content,
                         date=a_default_datetime()):
        self.add_trashinfo3(basename, path, date)
        make_file(self.file_path(basename), content)

    def a_trashinfo_path(self, basename):
        return os.path.join(self.info_path, '%s.trashinfo' % basename)

    def file_path(self, basename):
        return os.path.join(self.files_path, basename)

    def add_trashinfo_basename_path(self, basename, path):
        self.add_trashinfo3(basename, path, a_default_datetime())

    def add_trashinfo2(self, path, deletion_date):
        basename = str(uuid.uuid4())
        self.add_trashinfo3(basename, path, deletion_date)

    def add_trashinfo3(self, basename, path, deletion_date):
        content = trashinfo_content(path, deletion_date)
        self.add_trashinfo_content(basename, content)

    def add_a_valid_trashinfo(self):
        self.add_trashinfo4('file1', "2000-01-01")

    def add_trashinfo4(self, path, deletion_date_as_string):
        if isinstance(deletion_date_as_string, datetime.datetime):
            raise ValueError("Use a string instead: %s" %
                             repr(deletion_date_as_string.strftime('%Y-%m-%d %H:%M:%S')))

        basename = str(uuid.uuid4())
        deletion_date = parse_date(deletion_date_as_string)
        self.add_trashinfo3(basename, path, deletion_date)

    def add_trashinfo_with_date(self, basename, deletion_date):
        content = trashinfo_content2([
            ("DeletionDate", deletion_date.strftime('%Y-%m-%dT%H:%M:%S')),
        ])
        self.add_trashinfo_content(basename, content)

    def add_trashinfo_with_invalid_date(self, basename, invalid_date):
        content = trashinfo_content2([
            ("DeletionDate", invalid_date),
        ])
        self.add_trashinfo_content(basename, content)

    def add_trashinfo_without_path(self, basename):
        deletion_date = a_default_datetime()
        content = trashinfo_content2([
            ("DeletionDate", deletion_date.strftime('%Y-%m-%dT%H:%M:%S')),
        ])

        self.add_trashinfo_content(basename, content)

    def add_trashinfo_without_date(self, path):
        basename = str(uuid.uuid4())
        content = trashinfo_content2([
            ('Path', format_original_location(path)),
        ])

        self.add_trashinfo_content(basename, content)

    def add_trashinfo_wrong_date(self, path, wrong_date):
        basename = str(uuid.uuid4())
        content = trashinfo_content2([
            ('Path', format_original_location(path)),
            ("DeletionDate", wrong_date),
        ])

        self.add_trashinfo_content(basename, content)

    def add_trashinfo_content(self, basename, content):
        trashinfo_path = self.a_trashinfo_path(basename)
        make_parent_for(trashinfo_path)
        make_file(trashinfo_path, content)

    def ls_info(self):
        return os.listdir(self.info_path)

    def make_parent_sticky(self):
        make_sticky_dir(self.path.parent)

    def make_parent_unsticky(self):
        make_unsticky_dir(self.path.parent)

    def make_parent_symlink(self):
        is_a_symlink_to_a_dir(self.path.parent)

    def make_dir(self):
        os.mkdir(self.path)

    def does_not_exist(self):
        does_not_exist(self.path)


def trashinfo_content_default_date(path):
    return trashinfo_content(path, a_default_datetime())


def trashinfo_content(path, deletion_date):
    return trashinfo_content2([
        ('Path', format_original_location(path)),
        ("DeletionDate", deletion_date.strftime('%Y-%m-%dT%H:%M:%S')),
    ])


def trashinfo_content2(values):
    return ("[Trash Info]\n" +
            "".join("%s=%s\n" % (name, value) for name, value in values))
