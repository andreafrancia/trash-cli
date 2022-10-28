import datetime
import os
import uuid

from trashcli.put.forma_trash_info import format_original_location

from .support.files import make_file, make_parent_for, make_unreadable_file


def a_default_datetime():
    return datetime.datetime(2000, 1, 1, 0, 0, 1)


class FakeTrashDir:
    def __init__(self, path):
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
