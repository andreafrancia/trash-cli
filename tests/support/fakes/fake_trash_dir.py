import datetime
import os
import uuid
from typing import List, Tuple, NamedTuple, Self, Optional

from tests.support.dates import jan_11_2001
from tests.support.dirs.my_path import MyPath
from tests.support.files import does_not_exist
from tests.support.files import is_a_symlink_to_a_dir
from tests.support.files import make_file, make_parent_for, make_unreadable_file
from tests.support.files import make_sticky_dir
from tests.support.files import make_unsticky_dir
from tests.support.trashinfo.parse_date import parse_date
from trashcli.put.format_trash_info import format_original_location
from trashcli.put.janitor_tools.info_file_persister import TrashinfoData
from trashcli.restore.trashed_file import TrashedFile


def a_default_datetime():
    return datetime.datetime(2000, 1, 1, 0, 0, 1)


class TrashInfoPath(NamedTuple('TrashinfoPath', [
    ('info_basename', str),
    ('info_dir_path', str),
    ('copy_basename', str),
])):
    @property
    def info_full_path(self):
        return os.path.join(self.info_dir_path, self.info_basename)

class FakeTrashDirWithRoot:
    def __init__(
            self,
            trash_dir,  # type: FakeTrashDir
            root_dir,  # type: MyPath
                 ):
        self.trash_dir = trash_dir
        self.root_dir = root_dir

    def add_trashed_file(self, path):
        self.trash_dir.add_file_trashed_from_dir(path, self.root_dir)


class FakeTrashDir:
    def __init__(self, path):
        self.path = path
        self.info_path = os.path.join(path, 'info')
        self.files_path = os.path.join(path, 'files')

    def __truediv__(self,  # type: Self
                    other,  # type: str
                    ):  # type: (...) -> MyPath
        return self.path / other

    def add_unreadable_trashinfo(self, basename):
        info_path = self.a_trashinfo_path(basename)
        make_unreadable_file(info_path.info_full_path)

    def add_file_trashed_from_dir(self,
                                  name,  # type: str
                                  cwd,  # type: MyPath
                                  content=None,
                                  del_date=jan_11_2001(),
                                  # type: Optional[datetime.datetime]
                                  ):  # type: (...) -> TrashedFile
        original_location = cwd.join_no_slash(name)
        if content is None:
            content = 'content of ' + name
        return self.add_trashed_file(os.path.basename(name),
                                     original_location,
                                     content,
                                     del_date)

    def add_trashed_file(self,  # type: Self
                         basename,  # type: str
                         orig_loc,  # type: str
                         content,  # type: str
                         del_date=a_default_datetime()
                         # type: datetime.datetime
                         ):  # type: (...) -> TrashedFile
        trash_info_data = self.add_trashinfo3(basename, orig_loc, del_date)
        make_file(self.file_path(basename), content)

        return TrashedFile(
            original_location=orig_loc,
            deletion_date=del_date,
            info_file=trash_info_data.info_full_path,
            original_file=trash_info_data.original_file_path,
        )

    def a_trashinfo_path(self,
                         basename,  # type: str
                         ):  # type: (...) -> TrashInfoPath
        return TrashInfoPath(
            info_dir_path=self.info_path,
            info_basename='%s.trashinfo' % basename,
            copy_basename=basename,
        )

    def file_path(self, basename):
        return os.path.join(self.files_path, basename)

    def add_trashinfo_basename_path(self, basename, path):
        self.add_trashinfo3(basename, path, a_default_datetime())

    def add_trashinfo2(self, path, deletion_date):
        basename = str(uuid.uuid4())
        self.add_trashinfo3(basename, path, deletion_date)

    def add_trashinfo3(self,  # type: Self
                       basename,
                       path,
                       deletion_date
                       ):  # type: (...) -> TrashinfoData
        content = trashinfo_content(path, deletion_date)
        return self.add_trashinfo_content(basename, content)

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

    def add_trashinfo_content(self,  # type: Self
                              basename,
                              content,
                              ):  # type: (...) -> TrashinfoData
        trash_info_path = self.a_trashinfo_path(basename)
        info_full_path = trash_info_path.info_full_path
        make_parent_for(info_full_path)
        make_file(info_full_path, content)
        return TrashinfoData(
            content=content,
            info_dir_path=trash_info_path.info_dir_path,
            basename=trash_info_path.info_basename,
        )

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


def trashinfo_content(orig_location,  # type: str
                      deletion_date,  # type: datetime.datetime
                      ):
    return trashinfo_content2([
        ('Path', format_original_location(orig_location)),
        ("DeletionDate", deletion_date.strftime('%Y-%m-%dT%H:%M:%S')),
    ])


def trashinfo_content2(
        values,  # type: List[Tuple]
):  # type: (...) -> str
    return ("[Trash Info]\n" +
            "".join("%s=%s\n" % (name, value) for name, value in values))
