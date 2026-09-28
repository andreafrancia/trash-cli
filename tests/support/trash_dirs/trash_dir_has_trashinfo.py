from tests.support.restore.fake_restore_fs import FakePathFs
from trashcli.put.fs.fs import Fs


class TrashDirHasTrashInfo:
    def __init__(self,
                 fs,  # type: FakePathFs
                 home_trash,
                 volume_trash):
        self.fs = fs
        self.home_trash = home_trash
        self.volume_trash = volume_trash

    def has_a_well_formed_trashinfo(self, basename):
        self.fs.add_file('{home_trash}/info/{basename}'.format(basename=basename,
                                                               home_trash=self.home_trash),
                         b'[Trash Info]\n'
                         b'Path=name\n'
                         b'DeletionDate=2001-01-01T10:10:10\n')
        self.fs.add_file('{home_trash}/files/info_path'
                         .format(home_trash=self.home_trash),
                         b'contents')

    def has_a_non_trashinfo(self, basename):
        self.fs.add_file('{home_trash}/info/{basename}'
                         .format(basename=basename,
                                 home_trash=self.home_trash))

    def has_a_non_parseable_trashinfo(self, basename):
        self.fs.add_file('{home_trash}/info/{basename}'
                         .format(basename=basename,
                                 home_trash=self.home_trash), b'')

    def has_a_unreadable_trashinfo(self, basename):
        self.fs.fake_fs.makedirs('{home_trash}/info/{basename}'
                                 .format(basename=basename,
                                         home_trash=self.home_trash),
                                 0o755)

    def has_a_volume_trashinfo(self, name, path_line, content=None):
        content = content if content is not None else ''
        self.fs.add_file('{volume_path}/info/{name}.trashinfo'
                         .format(name=name, volume_path=self.volume_trash),
                         ('[Trash Info]\n'
                          'Path=%s\n'
                          'DeletionDate=2000-01-01T00:00:00\n' % path_line
                          ).encode('utf-8'))
        self.fs.add_file('{volume_path}/files/{name}'
                         .format(name=name, volume_path=self.volume_trash),
                         content)

    def remaining_trashinfo(self, trash_dir):
        return list(self.fs.list_files_in_dir(
            "{trash_dir}/info".format(trash_dir=trash_dir)))

    def remaining_original_copies(self, trash_dir):
        return list(self.fs.list_files_in_dir(
            "{trash_dir}/files".format(trash_dir=trash_dir)))
