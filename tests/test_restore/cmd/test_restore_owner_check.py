from tests.test_restore.components.collaborators.\
    test_restore_distrusts_unsafe_trash_dirs import (
        FakeReader, RecordingLogger, HOME, HOME_TRASH)
from trashcli.fstab.volumes import FakeVolumes2
from trashcli.restore.trash_directories import TrashDirectories1
from trashcli.trash_dirs_scanner import TopTrashDirRules


# the per-owner uid check was replaced by a per-directory rule: a trash dir is distrusted when its info or files sub-directory is a symlink or world writable
class TestRestoreOwnerCheck:
    def setup_method(self):
        self.volumes = FakeVolumes2("volume_of(%s)", [])
        self.logger = RecordingLogger()

    def home_trash_dirs(self, reader):
        td = TrashDirectories1(self.volumes, 123, {'HOME': HOME},
                               TopTrashDirRules(reader), self.logger)
        return [path for path, volume in td.all_trash_directories()]

    def test_entries_in_a_private_dir_are_readable_regardless_of_owner(self):
        # kept because the directory is safe, not because of the entry owner
        assert HOME_TRASH in self.home_trash_dirs(FakeReader())

    def test_a_world_writable_dir_is_skipped_regardless_of_owner(self):
        # the whole world-writable dir is skipped; ownership is not consulted
        reader = FakeReader(world_writable=[HOME_TRASH + '/info'])

        assert self.home_trash_dirs(reader) == []
