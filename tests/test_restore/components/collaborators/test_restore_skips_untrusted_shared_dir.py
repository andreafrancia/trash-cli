from trashcli.fstab.volumes import FakeVolumes2
from trashcli.restore.trash_directories import TrashDirectories1
from trashcli.trash_dirs_scanner import top_trash_dir_valid, \
    top_trash_dir_invalid_because_not_sticky


class TrustingReader:
    # never touches the disk; nothing is a symlink or world writable
    def is_symlink(self, path):
        return False

    def is_world_writable(self, path):
        return False


class NullLogger:
    def warning(self, message):
        pass


class FakeRules:
    def __init__(self, result):
        self.result = result
        self.reader = TrustingReader()

    def valid_to_be_read(self, path):
        return self.result


class TestRestoreSkipsUntrustedSharedDir:
    def setup_method(self):
        self.volumes = FakeVolumes2("volume_of(%s)", [])
        self.volumes.set_volumes(['/'])

    def readable_trash_dirs(self, rules):
        td = TrashDirectories1(self.volumes, 123, {'HOME': '~'}, rules,
                               NullLogger())
        return [path for path, volume in td.all_trash_directories()]

    def test_a_valid_shared_trash_dir_is_read(self):
        dirs = self.readable_trash_dirs(FakeRules(top_trash_dir_valid))

        assert '/.Trash/123' in dirs

    def test_an_untrusted_shared_trash_dir_is_skipped(self):
        dirs = self.readable_trash_dirs(
            FakeRules(top_trash_dir_invalid_because_not_sticky))

        assert '/.Trash/123' not in dirs
        assert '/.Trash-123' in dirs
        assert '~/.local/share/Trash' in dirs
