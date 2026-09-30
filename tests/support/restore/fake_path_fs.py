import os

from tests.support.fakes.fake_volume_path_fs import FakeVolumePathFs
from tests.support.put.fake_fs.failing_fake_fs import FailingFakeFs, \
    FailOnMoveFakeFs
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.fslib.protocols.path_exists import PathExists
from trashcli.fstab.volumes import FakeVolumes
from trashcli.restore.fs.protocols.restore_fs import RestoreFs


class FakePathFs(RestoreFs, PathExists, FakeVolumePathFs):

    def __init__(self):
        self.fake_fs = FailOnMoveFakeFs()
        self.mount_points = []

    def getcwd_as_realpath(self):
        return os.path.join('/', self.fake_fs.cwd)

    def exists(self, path):
        return self.path_exists(path)

    def path_exists(self, path):
        return self.fake_fs.exists(path)

    def is_sticky_dir(self, path):
        return self.fake_fs.is_sticky_dir(path)

    def is_symlink(self, path):
        return self.fake_fs.is_symlink(path)

    def is_world_writable(self, path):
        return self.fake_fs.is_world_writable(path)

    def set_sticky_bit(self, path):
        self.fake_fs.set_sticky_bit(path)

    def mkdirs(self, path):
        self.fake_fs.makedirs(path, 0o755)

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

    def list_files_in_dir(self, dir_path):
        for file_path in self.fake_fs.listdir(dir_path):
            yield os.path.join(dir_path, file_path)

    def contents_of(self, path):
        content = self.fake_fs.read(path)
        if type(content) is bytes:
            content = content.decode('utf-8')
        return content
