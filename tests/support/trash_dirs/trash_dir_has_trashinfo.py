import os

from typing import Optional

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.put.format_trash_info import format_trashinfo
from tests.support.restore.restore_fixture import RestoreFixture


class TrashDirHasTrashInfo:
    def __init__(self,
                 fs,  # type: FakeFs
                 fixture,  # type: RestoreFixture
                 home_trash=None,  # type: Optional[str]
                 volume_trash=None,  # type: Optional[str]
                 ):
        self.fs = fs
        self.fixture = fixture
        self.home_trash = home_trash
        self.volume_trash = volume_trash

    def add_file(self, path, content=b''):
        self.fs.makedirs(os.path.dirname(path), 0o755)
        self.fs.make_file(path, content)

    def add_trash_file(self, from_path, trash_dir, time,
                       original_file_content=''):
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path)
        info_path = os.path.join(trash_dir, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(trash_dir, 'files', basename)
        self.add_file(info_path, content)
        self.add_file(backup_copy_path, original_file_content.encode('utf-8'))

    def add_trash_empty_file(self, from_path, trash_dir, time):
        self.add_trash_file(from_path, trash_dir, time, '')

    def make_trashed_file(self, from_path, trash_dir, time,
                          original_file_content):
        return self.fixture.make_trashed_file(from_path, trash_dir, time,
                                         original_file_content)

    def has_a_well_formed_trashinfo(self,
                                    basename,  # type: str
                                    ):
        self.add_file('{home_trash}/info/{basename}'
                         .format(basename=basename,
                                 home_trash=self.home_trash),
                         b'[Trash Info]\n'
                         b'Path=name\n'
                         b'DeletionDate=2001-01-01T10:10:10\n')
        self.add_file('{home_trash}/files/info_path'
                         .format(home_trash=self.home_trash),
                         b'contents')

    def has_a_non_trashinfo(self,
                            basename,  # type: str
                            ):
        self.add_file('{home_trash}/info/{basename}'
                         .format(basename=basename,
                                 home_trash=self.home_trash))

    def has_a_non_parseable_trashinfo(self,
                                      basename,  # type: str
                                      ):
        self.add_file('{home_trash}/info/{basename}'
                         .format(basename=basename,
                                 home_trash=self.home_trash), b'')

    def has_a_unreadable_trashinfo(self,
                                   basename,  # type: str
                                   ):
        self.fs.makedirs('{home_trash}/info/{basename}'
                                 .format(basename=basename,
                                         home_trash=self.home_trash),
                                 0o755)

    def has_a_volume_trashinfo(self,
                               name,  # type: str
                               path_line,  # type: str
                               content=None,  # type: Optional[str]
                               ):
        content = content if content is not None else ''
        self.add_file('{volume_path}/info/{name}.trashinfo'
                         .format(name=name, volume_path=self.volume_trash),
                         ('[Trash Info]\n'
                          'Path=%s\n'
                          'DeletionDate=2000-01-01T00:00:00\n' % path_line
                          ).encode('utf-8'))
        self.add_file('{volume_path}/files/{name}'
                         .format(name=name, volume_path=self.volume_trash),
                         content)

    def remaining_trashinfo(self,
                            trash_dir,  # type: str
                            ):
        return list(self.fs.list_files_in_dir(
            "{trash_dir}/info".format(trash_dir=trash_dir)))

    def remaining_original_copies(self,
                                  trash_dir,  # type: str
                                  ):
        return list(self.fs.list_files_in_dir(
            "{trash_dir}/files".format(trash_dir=trash_dir)))
