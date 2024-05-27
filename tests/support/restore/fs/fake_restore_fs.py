import os
from typing import Iterable
from typing import List

from six import binary_type

from tests.support.restore.fs.fs_state import FsState
from tests.support.trash_dirs.trash_dir_fixture import TrashDirFixture
from trashcli.fstab.volumes import FakeVolumes
from trashcli.put.fs.fs import Fs
from trashcli.restore.fs.restore_fs import RestoreFs


class FakeRestoreFs(RestoreFs):

    def __init__(self,
                 fs,  # type: Fs
                 ):
        self.fs = fs
        self.mount_points = []  # type: List[str]

    def exists(self, path):
        return self.fs.exists(path)

    def list_files_in_dir(self, path):  # type: (str) -> Iterable[str]
        return self.fs.list_files_in_dir(path)

    def mkdirs(self, path):
        self.fs.makedirs(path, 755)

    def move(self, path, dest):
        self.fs.move(path, dest)

    def remove_file(self, path):
        self.fs.remove_file(path)

    def write_file(self, path,
                   content,  # type: binary_type
                   ):  # type: (...) -> None
        self.fs.make_file(path, content)


    def read_file(self, path,
             ):  # type: (...) -> binary_type
        return self.fs.read_file(path)

    def save_state(self):
        return FsState(self.fs)

    def list_all(self):
        return FsState(self.fs).describe_all()

    def add_volume(self, mount_point):
        self.mount_points.append(mount_point)

    def list_mount_points(self):
        return FakeVolumes(self.mount_points).list_mount_points()

    def volume_of(self, path):
        return FakeVolumes(self.mount_points).volume_of(path)

    def make_trashed_file(self,
                          from_path,
                          trash_dir,
                          time,
                          original_file_content,  # type: binary_type
                          ):
        return TrashDirFixture(self.fs, trash_dir).make_trashed_file(
            from_path, time, original_file_content
        )

    def add_trash_file(self, from_path, trash_dir, time, original_file_content):
        TrashDirFixture(self.fs, trash_dir).add_trash_file(
            from_path, time, original_file_content
        )

    def add_file(self, path, content=b''):
        self.fs.make_file_p(path, content)

