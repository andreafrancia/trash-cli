from tests.support.dates import date_at
from tests.support.restore.fake_path_fs import FakePathFs
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger

HOME = '/home/user'
HOME_TRASH = '/home/user/.local/share/Trash'


class TestRestoreDistrustsUnsafeTrashDirs:
    def setup_method(self):
        self.fs = FakePathFs()
        self.fs.add_trash_file(HOME + "/foo", HOME_TRASH,
                               date_at(2018, 1, 1), '')
        self.user = RestoreUser(environ={'HOME': HOME},
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

    def restore_output(self):
        return self.user.run_restore([], from_dir=HOME).output()

    def make_symlink_to_the_content_of(self, path):
        # the content of path is moved elsewhere and path becomes a symlink to it
        self.fs.fake_fs.move(path, '/elsewhere')
        self.fs.fake_fs.symlink('/elsewhere', path)

    def test_a_normal_home_trash_is_kept(self):
        assert HOME + "/foo" in self.restore_output()

    def test_a_symlinked_info_dir_is_skipped(self):
        self.make_symlink_to_the_content_of(HOME_TRASH + '/info')

        assert (self.restore_output() ==
                "No files trashed from current dir ('%s')\n" % HOME)

    def test_a_world_writable_files_dir_is_skipped(self):
        self.fs.fake_fs.chmod(HOME_TRASH + '/files', 0o777)

        assert (self.restore_output() ==
                "No files trashed from current dir ('%s')\n" % HOME)

    def test_the_reason_a_dir_is_skipped_is_reported(self):
        self.fs.fake_fs.chmod(HOME_TRASH + '/info', 0o777)

        self.user.run_restore([], from_dir=HOME)

        assert self.user.logger.captured == [
            "WARN: TrashDir skipped because its info dir is world writable: %s"
            % HOME_TRASH]
