from trashcli.fstab.volumes import FakeVolumes2
from trashcli.restore.trash_directories import TrashDirectories1
from trashcli.trash_dirs_scanner import TopTrashDirRules

HOME = '/home/user'
HOME_TRASH = '/home/user/.local/share/Trash'


class FakeReader:
    # a reader that never touches the disk; unlisted paths are trusted
    def __init__(self, symlinks=(), world_writable=()):
        self.symlinks = set(symlinks)
        self.world_writable = set(world_writable)

    def exists(self, path):
        return True

    def is_sticky_dir(self, path):
        return True

    def is_symlink(self, path):
        return path in self.symlinks

    def is_world_writable(self, path):
        return path in self.world_writable


class RecordingLogger:
    def __init__(self):
        self.warnings = []

    def warning(self, message):
        self.warnings.append(message)


class TestRestoreDistrustsUnsafeTrashDirs:
    def setup_method(self):
        self.volumes = FakeVolumes2("volume_of(%s)", [])
        self.logger = RecordingLogger()

    def trusted_home_trash_dirs(self, reader):
        rules = TopTrashDirRules(reader)
        td = TrashDirectories1(self.volumes, 123, {'HOME': HOME}, rules,
                               self.logger)
        return [path for path, volume in td.all_trash_directories()]

    def test_a_normal_home_trash_is_kept(self):
        assert HOME_TRASH in self.trusted_home_trash_dirs(FakeReader())

    def test_a_symlinked_info_dir_is_skipped(self):
        reader = FakeReader(symlinks=[HOME_TRASH + '/info'])

        assert self.trusted_home_trash_dirs(reader) == []

    def test_a_world_writable_files_dir_is_skipped(self):
        reader = FakeReader(world_writable=[HOME_TRASH + '/files'])

        assert self.trusted_home_trash_dirs(reader) == []

    def test_the_reason_a_dir_is_skipped_is_reported(self):
        reader = FakeReader(world_writable=[HOME_TRASH + '/info'])

        self.trusted_home_trash_dirs(reader)

        assert self.logger.warnings == [
            "TrashDir skipped because its info dir is world writable: %s"
            % HOME_TRASH]
