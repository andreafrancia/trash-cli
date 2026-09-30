from tests.support.put.dummy_clock import jan_1st_2024
from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.restore_fixture import RestoreFixture
from tests.support.trash_dirs.trash_dir_has_trashinfo import \
    TrashDirHasTrashInfo
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger


class TestRestoreUsesAllTheTrashDirectories:
    # Test that trash-restore will search in all trash directories for trash.
    # The trash directories can be:
    #   - home trash directory,
    #   - volume trash dirs (method 1)
    #   - volume trash dirs (method 2)
    def setup_method(self):
        self.fs = FakeFs()
        self.fixture = RestoreFixture(self.fs)
        self.trash = TrashDirHasTrashInfo(self.fs, self.fixture)
        self.fs.add_volume('/')
        self.fs.add_volume('/mnt')
        self.log_messages = []
        self.user = RestoreUser(environ={'HOME': '/home/user'},
                                uid=123,
                                file_reader=self.fs,
                                path_read_fs=self.fs,
                                write_fs=self.fs,
                                listing_fs=self.fs,
                                version='1.0',
                                volumes=self.fs,
                                volume_path_fs=self.fs,
                                top_trash_dir_rules_reader=self.fs,
                                logger=RecordingLogger(self.log_messages))
        self.home_trash = '/home/user/.local/share/Trash'

    def test_files_from_every_trash_directory_are_listed(self):
        # One trashed file per directory that all_trash_directories() is
        # expected to yield for volumes ['/', '/mnt'] and uid 123:
        #   HOME_TRASH      the home trash
        #   /.Trash/123     shared trash on volume '/'
        #   /.Trash-123     private trash on volume '/'
        #   /mnt/.Trash/123 shared trash on volume '/mnt'
        #   /mnt/.Trash-123 private trash on volume '/mnt'
        self.trash.add_trash_file('/home/user/home_file', self.home_trash,
                               jan_1st_2024())
        self.trash.add_trash_file('/root_shared_file', '/.Trash/123',
                               jan_1st_2024())
        self.trash.add_trash_file('/root_private_file', '/.Trash-123',
                               jan_1st_2024())
        # Path= must be relative for volume trashes on a non-root volume.
        self.trash.add_trash_file('mnt_shared_file', '/mnt/.Trash/123',
                               jan_1st_2024())
        self.trash.add_trash_file('mnt_private_file', '/mnt/.Trash-123',
                               jan_1st_2024())
        # A shared trash dir ($topdir/.Trash/$uid) is only valid_to_be_read
        # when its parent ($topdir/.Trash) is sticky, per TopTrashDirRules.
        self.fs.set_sticky_bit('/.Trash')
        self.fs.set_sticky_bit('/mnt/.Trash')

        # explicit '/' path argument (rather than an implicit cwd of '/',
        # which triggers a '//' path-joining quirk) to match every trashed
        # file regardless of its original location
        res = self.user.run_restore(['trash-restore', '/'], from_dir='/')

        output = res.output()
        assert '/home/user/home_file' in output
        assert '/root_shared_file' in output
        assert '/root_private_file' in output
        assert '/mnt/mnt_shared_file' in output
        assert '/mnt/mnt_private_file' in output
        assert len(output.splitlines()) == 6  # 5 listed files + prompt result
        assert self.log_messages == []
