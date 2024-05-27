import datetime
import os
import uuid
from typing import List
from typing import Tuple

from six import binary_type

from tests.support.fs_fixture import FsFixture
from tests.support.trashinfo.parse_date import parse_date
from trashcli.lib import TrashInfoContent
from trashcli.put.format_trash_info import format_original_location
from trashcli.put.fs.real_fs import RealFs


def a_default_datetime():
    return datetime.datetime(2000, 1, 1, 0, 0, 1)


def trashinfo_content_default_date(path,
                                   ):  # type: (...) -> TrashInfoContent
    return trashinfo_content(path, a_default_datetime())


def trashinfo_content(path,
                      deletion_date,  # type: datetime.datetime
                      ):  # type: (...) -> TrashInfoContent
    return trashinfo_content2([
        (b'Path', format_original_location(path)),
        (b"DeletionDate",
         deletion_date.strftime('%Y-%m-%dT%H:%M:%S').encode('utf-8')),
    ])


def trashinfo_content2(values,
                       # type: List[Tuple[TrashInfoContent, TrashInfoContent]]
                       ):  # type: (...) -> TrashInfoContent
    return (b"[Trash Info]\n" +
            b"".join(b"%s=%s\n" % (name, value) for name, value in values))


class FakeTrashDir:
    def __init__(self, path):
        self.path = path
        self.info_path = os.path.join(path, 'info')
        self.files_path = os.path.join(path, 'files')
        self.fs = FsFixture(RealFs())

    def add_unreadable_trashinfo(self, basename):
        path = self.a_trashinfo_path(basename)
        self.fs.make_unreadable_file(path)

    def add_trashed_file(self,
                         basename,
                         path,
                         content,  # type: binary_type
                         date=a_default_datetime(),
                         ):  # type: (...) -> None
        self.add_trashinfo3(basename, path, date)
        self.fs.make_file(self.file_path(basename), content)

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
                             repr(deletion_date_as_string.strftime(
                                 '%Y-%m-%d %H:%M:%S')))

        basename = str(uuid.uuid4())
        deletion_date = parse_date(deletion_date_as_string)
        self.add_trashinfo3(basename, path, deletion_date)

    def add_trashinfo_with_date(self, basename, deletion_date):
        content = trashinfo_content2([
            (b"DeletionDate",
             deletion_date.strftime('%Y-%m-%dT%H:%M:%S').encode('utf-8')),
        ])
        self.add_trashinfo_content(basename, content)

    def add_trashinfo_with_invalid_date(self, basename, invalid_date):
        content = trashinfo_content2([
            (b"DeletionDate", invalid_date),
        ])
        self.add_trashinfo_content(basename, content)

    def add_trashinfo_without_path(self, basename):
        deletion_date = a_default_datetime()
        content = trashinfo_content2([
            (b"DeletionDate",
             deletion_date.strftime('%Y-%m-%dT%H:%M:%S').encode('utf-8')),
        ])

        self.add_trashinfo_content(basename, content)

    def add_trashinfo_without_date(self, path):
        basename = str(uuid.uuid4())
        content = trashinfo_content2([
            (b'Path', format_original_location(path)),
        ])

        self.add_trashinfo_content(basename, content)

    def add_trashinfo_wrong_date(self, path,
                                 wrong_date,  # type: TrashInfoContent
                                 ):  # type: (...) -> None
        basename = str(uuid.uuid4())
        content = trashinfo_content2([
            (b'Path', format_original_location(path)),
            (b"DeletionDate", wrong_date),
        ])

        self.add_trashinfo_content(basename, content)

    def add_trashinfo_content(self, basename,
                              content,  # type: TrashInfoContent
                              ):  # type: (...) -> None
        trashinfo_path = self.a_trashinfo_path(basename)
        self.fs.make_parent_for(trashinfo_path)
        self.fs.make_file(trashinfo_path, content)

    def ls_info(self):
        return self.fs.listdir(self.info_path)

    def make_parent_sticky(self):
        self.fs.make_sticky_dir(self.path.parent)

    def make_parent_unsticky(self):
        self.fs.make_unsticky_dir(self.path.parent)

    def make_parent_symlink(self):
        self.fs.make_a_symlink_to_a_dir(self.path.parent)

    def make_dir(self):
        self.fs.make_dir(self.path)

    def does_not_exist(self):
        assert not self.fs.exists(self.path)

    def list_trash_dir(self):
        return _list_trash_dir(self.path)


def _list_trash_dir(trash_dir_path):
    return (_list_files_in_subdir(trash_dir_path, 'info') +
            _list_files_in_subdir(trash_dir_path, 'files'))


def _list_files_in_dir(path):
    if not os.path.isdir(path):
        return []
    return os.listdir(path)


def _list_files_in_subdir(path, subdir):
    return ["%s/%s" % (subdir, f) for f in _list_files_in_dir(path / subdir)]
