from tests.support.dates import date_at
from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.trash_dirs.given_trash import \
    GivenTrash
from tests.test_restore.cmd.test_restore_distrusts_unsafe_trash_dirs import (
        HOME, HOME_TRASH)
from tests.test_restore.support.recording_logger import RecordingLogger
from tests.support.fakes.fake_volumes2 import FakeVolumesFs2
from trashcli.restore.trash_directories import TrashDirectories1
from trashcli.trash_dirs_scanner import TopTrashDirRules


# the per-owner uid check was replaced by a per-directory rule: a trash dir is distrusted when its info or files sub-directory is a symlink or world writable
class TestRestoreOwnerCheck:
    def setup_method(self):
        self.volumes = FakeVolumesFs2("volume_of(%s)", [])
        self.logger = RecordingLogger()
        self.fs = FakeFs()
        self.trash = GivenTrash(self.fs)
        self.trash.has_trashed_file(HOME + "/foo", HOME_TRASH,
                                    date_at(2018, 1, 1), '')

    def home_trash_dirs(self):
        td = TrashDirectories1(self.volumes, 123, {'HOME': HOME},
                               TopTrashDirRules(self.fs), self.logger)
        return [path for path, volume in td.all_trash_directories()]

    def test_entries_in_a_private_dir_are_readable_regardless_of_owner(self):
        # kept because the directory is safe, not because of the entry owner
        assert HOME_TRASH in self.home_trash_dirs()

    def test_a_world_writable_dir_is_skipped_regardless_of_owner(self):
        # the whole world-writable dir is skipped; ownership is not consulted
        self.fs.chmod(HOME_TRASH + '/info', 0o777)

        assert self.home_trash_dirs() == []
