import unittest

from trashcli.fstab.volumes import FakeVolumes2
from trashcli.restore.trash_directories import TrashDirectories1
from trashcli.trash_dirs_scanner import top_trash_dir_valid, \
    top_trash_dir_invalid_because_not_sticky


class NoSymlinks:
    def is_symlink(self, path):
        return False


class NullLogger:
    def warning(self, message):
        pass


class FakeRules:
    reader = NoSymlinks()

    def __init__(self, result):
        self.result = result

    def valid_to_be_read(self, path):
        return self.result


class TestRestoreSkipsUntrustedSharedDir(unittest.TestCase):
    def setUp(self):
        self.environ = {'HOME': '~'}
        self.volumes = FakeVolumes2("volume_of(%s)", [])
        self.volumes.set_volumes(['/'])

    def _dirs(self, rules):
        td = TrashDirectories1(self.volumes, 123, self.environ, rules,
                               NullLogger())
        return [path for path, volume in td.all_trash_directories()]

    def test_a_valid_shared_trash_dir_is_read(self):
        dirs = self._dirs(FakeRules(top_trash_dir_valid))

        assert '/.Trash/123' in dirs

    def test_an_untrusted_shared_trash_dir_is_skipped(self):
        dirs = self._dirs(FakeRules(top_trash_dir_invalid_because_not_sticky))

        assert '/.Trash/123' not in dirs
        assert '/.Trash-123' in dirs
        assert '~/.local/share/Trash' in dirs
