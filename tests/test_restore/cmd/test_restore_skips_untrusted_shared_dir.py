from tests.support.dates import date_at
from tests.support.restore.fake_restore_fs import FakePathFs
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger

HOME = '/home/user'
HOME_TRASH = '/home/user/.local/share/Trash'
SHARED_TRASH = '/.Trash/123'
PRIVATE_TRASH = '/.Trash-123'


class FakeReader:
    # a reader that never touches the disk; unlisted paths are trusted
    def __init__(self, sticky_dirs=(), symlinks=(), world_writable=()):
        self.sticky_dirs = set(sticky_dirs)
        self.symlinks = set(symlinks)
        self.world_writable = set(world_writable)

    def exists(self, path):
        return True

    def is_sticky_dir(self, path):
        return path in self.sticky_dirs

    def is_symlink(self, path):
        return path in self.symlinks

    def is_world_writable(self, path):
        return path in self.world_writable


class TestRestoreSkipsUntrustedSharedDir:
    def setup_method(self):
        self.fs = FakePathFs()
        self.fs.add_volume('/')
        self.fs.add_trash_file(HOME + "/from-home", HOME_TRASH,
                               date_at(2018, 1, 1), '')
        self.fs.add_trash_file("/from-shared", SHARED_TRASH,
                               date_at(2018, 1, 1), '')
        self.fs.add_trash_file("/from-private", PRIVATE_TRASH,
                               date_at(2018, 1, 1), '')

    def restore_output(self, reader):
        user = RestoreUser(environ={'HOME': HOME},
                           uid=123,
                           file_reader=self.fs,
                           path_read_fs=self.fs,
                           write_fs=self.fs,
                           listing_fs=self.fs,
                           version='1.0',
                           volumes=self.fs,
                           volume_path_fs=self.fs,
                           top_trash_dir_rules_reader=reader,
                           logger=RecordingLogger())
        res = user.run_restore(['trash-restore', '/'], from_dir=HOME)
        return res.output()

    def test_a_valid_shared_trash_dir_is_read(self):
        # the parent of the shared trash dir (.Trash) is sticky, so it is trusted
        reader = FakeReader(sticky_dirs=['/.Trash'])

        assert '/from-shared' in self.restore_output(reader)

    def test_an_untrusted_shared_trash_dir_is_skipped(self):
        # the parent of the shared trash dir (.Trash) is not sticky, so it is distrusted
        reader = FakeReader(sticky_dirs=[])

        output = self.restore_output(reader)

        assert '/from-shared' not in output
        assert '/from-private' in output
        assert HOME + '/from-home' in output
