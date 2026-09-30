from tests.support.dates import date_at
from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.trash_dirs.trash_dir_has_trashinfo import \
    TrashDirHasTrashInfo
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger

HOME = '/home/user'
HOME_TRASH = '/home/user/.local/share/Trash'
SHARED_TRASH = '/.Trash/123'
PRIVATE_TRASH = '/.Trash-123'


class TestRestoreSkipsUntrustedSharedDir:
    def setup_method(self):
        self.fs = FakeFs()
        self.trash = TrashDirHasTrashInfo(self.fs)
        self.fs.add_volume('/')
        self.trash.add_trash_file(HOME + "/from-home", HOME_TRASH,
                               date_at(2018, 1, 1), '')
        self.trash.add_trash_file("/from-shared", SHARED_TRASH,
                               date_at(2018, 1, 1), '')
        self.trash.add_trash_file("/from-private", PRIVATE_TRASH,
                               date_at(2018, 1, 1), '')

    def restore_output(self):
        user = RestoreUser(environ={'HOME': HOME},
                           uid=123,
                           file_reader=self.fs,
                           path_read_fs=self.fs,
                           write_fs=self.fs,
                           listing_fs=self.fs,
                           version='1.0',
                           volumes=self.fs,
                           volume_path_fs=self.fs,
                           top_trash_dir_rules_reader=self.fs,
                           logger=RecordingLogger())
        res = user.run_restore(['trash-restore', '/'], from_dir=HOME)
        return res.output()

    def test_a_valid_shared_trash_dir_is_read(self):
        # the parent of the shared trash dir (.Trash) is sticky, so it is trusted
        self.fs.set_sticky_bit('/.Trash')

        assert '/from-shared' in self.restore_output()

    def test_an_untrusted_shared_trash_dir_is_skipped(self):
        # the parent of the shared trash dir (.Trash) is not sticky, so it is distrusted
        output = self.restore_output()

        assert '/from-shared' not in output
        assert '/from-private' in output
        assert HOME + '/from-home' in output

    def test_a_shared_trash_dir_under_a_symlinked_parent_is_skipped(self):
        # the parent of the shared trash dir (.Trash) is sticky, but it is a
        # symlink: it could be redirected anywhere, so it is distrusted
        self.fs.move('/.Trash', '/elsewhere')
        self.fs.set_sticky_bit('/elsewhere')
        self.fs.symlink('/elsewhere', '/.Trash')

        output = self.restore_output()

        assert '/from-shared' not in output
        assert '/from-private' in output
        assert HOME + '/from-home' in output
