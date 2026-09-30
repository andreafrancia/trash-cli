from typing import Optional

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.restore_fixture import RestoreFixture


class TrashDirHasTrashInfo:
    def __init__(self,
                 fs,  # type: FakeFs
                 fixture,  # type: RestoreFixture
                 home_trash,  # type: str
                 volume_trash,  # type: str
                 ):
        self.fs = fs
        self.fixture = fixture
        self.home_trash = home_trash
        self.volume_trash = volume_trash

    def has_a_well_formed_trashinfo(self,
                                    basename,  # type: str
                                    ):
        self.fixture.add_file('{home_trash}/info/{basename}'
                         .format(basename=basename,
                                 home_trash=self.home_trash),
                         b'[Trash Info]\n'
                         b'Path=name\n'
                         b'DeletionDate=2001-01-01T10:10:10\n')
        self.fixture.add_file('{home_trash}/files/info_path'
                         .format(home_trash=self.home_trash),
                         b'contents')

    def has_a_non_trashinfo(self,
                            basename,  # type: str
                            ):
        self.fixture.add_file('{home_trash}/info/{basename}'
                         .format(basename=basename,
                                 home_trash=self.home_trash))

    def has_a_non_parseable_trashinfo(self,
                                      basename,  # type: str
                                      ):
        self.fixture.add_file('{home_trash}/info/{basename}'
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
        self.fixture.add_file('{volume_path}/info/{name}.trashinfo'
                         .format(name=name, volume_path=self.volume_trash),
                         ('[Trash Info]\n'
                          'Path=%s\n'
                          'DeletionDate=2000-01-01T00:00:00\n' % path_line
                          ).encode('utf-8'))
        self.fixture.add_file('{volume_path}/files/{name}'
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
