from tests.support.dates import date_at
from tests.support.restore.fake_restore_fs import FakePathFs
from tests.support.restore.restore_user import RestoreUser

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


class TestRestoreDistrustsUnsafeTrashDirs:
    def setup_method(self):
        self.fs = FakePathFs()
        self.fs.add_trash_file(HOME + "/foo", HOME_TRASH,
                               date_at(2018, 1, 1), '')

    def make_user(self, reader):
        return RestoreUser(environ={'HOME': HOME},
                           uid=123,
                           file_reader=self.fs,
                           path_read_fs=self.fs,
                           write_fs=self.fs,
                           listing_fs=self.fs,
                           version='1.0',
                           volumes=self.fs,
                           volume_path_fs=self.fs,
                           top_trash_dir_rules_reader=reader)

    def restore_output(self, reader):
        user = self.make_user(reader)
        res = user.run_restore([], from_dir=HOME)
        return res.output()

    def test_a_normal_home_trash_is_kept(self):
        assert HOME + "/foo" in self.restore_output(FakeReader())

    def test_a_symlinked_info_dir_is_skipped(self):
        reader = FakeReader(symlinks=[HOME_TRASH + '/info'])

        assert (self.restore_output(reader) ==
               "No files trashed from current dir ('%s')\n" % HOME)

    def test_a_world_writable_files_dir_is_skipped(self):
        reader = FakeReader(world_writable=[HOME_TRASH + '/files'])

        assert (self.restore_output(reader) ==
               "No files trashed from current dir ('%s')\n" % HOME)

    def test_the_reason_a_dir_is_skipped_is_reported(self):
        reader = FakeReader(world_writable=[HOME_TRASH + '/info'])
        user = self.make_user(reader)

        user.run_restore([], from_dir=HOME)

        assert user.logger.captured == [
            "WARN: TrashDir skipped because its info dir is world writable: %s"
            % HOME_TRASH]


