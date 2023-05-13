import os

from tests.test_put.support.fake_fs.fake_fs import FakeFs
from tests.test_restore.support.a_trashed_file import ATrashedFile
from trashcli.fs import PathExists
from trashcli.fstab.volumes import Volumes, FakeVolumes
from trashcli.put.format_trash_info import format_trashinfo
from trashcli.restore.file_system import ListingFileSystem, FileReader, \
    RestoreWriteFileSystem, RestoreReadFileSystem


class FakeRestoreFs(ListingFileSystem,
                    Volumes, FileReader, RestoreWriteFileSystem,
                    RestoreReadFileSystem, PathExists):

    def exists(self, path):
        return self.path_exists(path)

    def path_exists(self, path):
        return self.fake_fs.exists(path)

    def __init__(self):
        self.fake_fs = FakeFs()
        self.mount_points = []

    def mkdirs(self, path):
        self.fake_fs.makedirs(path, 755)

    def move(self, path, dest):
        self.fake_fs.move(path, dest)

    def remove_file(self, path):
        self.fake_fs.remove_file(path)

    def add_volume(self, mount_point):
        self.mount_points.append(mount_point)

    def list_mount_points(self):
        return FakeVolumes(self.mount_points).list_mount_points()

    def volume_of(self, path):
        return FakeVolumes(self.mount_points).volume_of(path)


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

    def add_trash_file(self, from_path, trash_dir, time, original_file_content):
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path)
        info_path = os.path.join(trash_dir, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(trash_dir, 'files', basename)
        self.add_file(info_path, content)
        self.add_file(backup_copy_path, original_file_content.encode('utf-8'))

    def add_file(self, path, content=b''):
        self.fake_fs.makedirs(os.path.dirname(path), 755)
        self.fake_fs.make_file(path, content)

    def list_files_in_dir(self, dir_path):
        for file_path in self.fake_fs.listdir(dir_path):
            yield os.path.join(dir_path, file_path)

    def contents_of(self, path):
        return self.fake_fs.read(path).decode('utf-8')
