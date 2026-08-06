import unittest

from trashcli.fstab.fake.fake_volumes import FakeVolumes
from trashcli.restore.trash_directories import TrashDirectories1
from trashcli.trash_dirs_scanner import top_trash_dir_valid


class NoSymlinks:
    def is_symlink(self, path):
        return False

    def is_world_writable(self, path):
        return False


class AlwaysValid:
    reader = NoSymlinks()

    def valid_to_be_read(self, path):
        return top_trash_dir_valid


class NullLogger:
    def warning(self, message):
        pass


class TestTrashDirectories(unittest.TestCase):
    def setUp(self):
        environ = {'HOME': '/volume_of_home/user_home'}
        self.volumes = FakeVolumes([])
        self.trash_directories = TrashDirectories1(self.volumes, 123, environ,
                                                   AlwaysValid(), NullLogger())

    def test_list_all_directories(self):
        self.volumes.set_volumes(['/', '/mnt', "/volume_of_home"])

        result = sorted(self.trash_directories.all_trash_directories())

        assert (result == [
            ('/.Trash-123', '/'),
            ('/.Trash/123', '/'),
            ('/mnt/.Trash-123', '/mnt'),
            ('/mnt/.Trash/123', '/mnt'),
            ('/volume_of_home/.Trash-123', '/volume_of_home'),
            ('/volume_of_home/.Trash/123', '/volume_of_home'),
            ('/volume_of_home/user_home/.local/share/Trash', '/volume_of_home'),
        ])
