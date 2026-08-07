import os
from typing import Iterable

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.a_trashed_file import ATrashedFile
from trashcli.fslib.fs_operations import PathExists, ListFilesInDir
from trashcli.fstab.volumes import Volumes
from trashcli.fstab.fake.fake_volumes import FakeVolumes
from trashcli.put.format_trash_info import format_trashinfo
from trashcli.restore.fs.restore_write_fs import RestoreWriterFs
from trashcli.restore.fs.path_reader_fs import PathReaderFs
from trashcli.restore.fs.file_reader_fs import FileReaderFs


class GivenFs:
    def __init__(self,
                 fake_fs,  # type: FakePathFs
                 ):
        self.fake_fs = fake_fs

    def add_volume(self, mount_point):
        self.fake_fs.add_volume(mount_point)

    def add_file(self, path, content=b''):
        self.fake_fs.makedirs(os.path.dirname(path), 755)
        self.fake_fs.make_file(path, content)

    def add_trash_file(self, from_path, trash_dir, time, original_file_content):
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path)
        info_path = os.path.join(trash_dir, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(trash_dir, 'files', basename)
        self.add_file(info_path, content)
        self.add_file(backup_copy_path, original_file_content.encode('utf-8'))

    def add_file_trashed_at(self, original_location, deletion_date):
        self.make_trashed_file(original_location, '/home/user/.local/share/Trash',
                               deletion_date, '')

    def make_trashed_file(self, from_path, trash_dir, time,
                          original_file_content):
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path)
        info_path = os.path.join(trash_dir, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(trash_dir, 'files', basename)
        trashed_file = ATrashedFile(trashed_from=from_path,
                                    info_file=info_path,
                                    backup_copy=backup_copy_path)
        self.add_file(info_path, content)
        self.add_file(backup_copy_path, original_file_content.encode('utf-8'))
        return trashed_file


class FakePathFs(ListFilesInDir,
                 Volumes, FileReaderFs, RestoreWriterFs,
                 PathReaderFs, PathExists):

    def __init__(self):
        self.fake_fs = FakeFs()

    def path_exists(self, path):
        return self.fake_fs.path_exists(path)

    def makedirs(self, path, mode):
        return self.fake_fs.makedirs(path, mode)

    def make_file(self, path, content):
        return self.fake_fs.make_file(path, content)

    def mkdirs(self, path):
        self.fake_fs.mkdirs(path)

    def move(self, path, dest):
        self.fake_fs.move(path, dest)

    def remove_file(self, path):
        self.fake_fs.remove_file(path)

    def add_volume(self, mount_point):
        return self.fake_fs.add_volume(mount_point)

    def list_volumes(self, environ):
        return self.fake_fs.list_volumes(environ)

    def is_mount(self, path):
        return self.fake_fs.is_mount(path)

    def volume_of(self, path):
        return self.fake_fs.volume_of(path)

    def list_files_in_dir(self, dir_path):  # type: (str) -> Iterable[str]
        return self.fake_fs.list_files_in_dir(dir_path)

    def contents_of(self, path):
        return self.fake_fs.contents_of(path)
