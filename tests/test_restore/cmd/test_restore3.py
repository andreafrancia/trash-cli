import sys
from typing import TypeVar

from six import StringIO

from tests.support.cmd.capture_exit_code2 import capture_exit_code2
from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.py2mock import Mock
from tests.test_restore.support.capture_logger import CaptureLogger
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fslib.real_fs_operations import RealListFilesInDir
from trashcli.fstab.volumes import FakeVolumes
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.real_restore_fs import RealRestoreWriterFs, \
    RealPathReaderFs, RealFileReaderFs
from tests.test_restore.support.fake_read_cwd import FakeReadCwdFs
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trashed_files import TrashedFiles

Self = TypeVar('Self', bound='TestTrashedFileRestoreIntegration')


class TestTrashedFileRestoreIntegration:

    @staticmethod
    def setup_trash_dir(home_dir):
        trash_dir = home_dir.mkdir_rel_p('.local/share/Trash')
        return FakeTrashDir(trash_dir)

    @staticmethod
    def setup_home_dir(root_dir):
        return root_dir.mkdir_rel_p("home/user")

    @staticmethod
    def setup_cwd(root_dir):
        return root_dir.mkdir_rel_p("cwd")

    def setup_method(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.input = HardCodedInput()
        self.temp_dir = MyPath.make_temp_dir()

        self.root_dir = self.temp_dir
        self.cwd = self.setup_cwd(self.root_dir)
        self.home_dir = self.setup_home_dir(self.root_dir)
        self.trash_dir = self.setup_trash_dir(self.home_dir)

        uid = 1000
        self.env = {'HOME': self.home_dir}
        # end of unix-like env

        self.logger = CaptureLogger()
        self.trashed_files = Mock(spec=TrashedFiles)
        self.cmd = RestoreCmd(
            stdout=self.stdout,
            stderr=self.stderr,
            exit=sys.exit,
            input=self.input,
            version="0.0.0",
            listing_fs=RealListFilesInDir(),
            read_fs=RealPathReaderFs(),
            write_fs=RealRestoreWriterFs(),
            read_cwd=FakeReadCwdFs(self.cwd),
            file_reader=RealFileReaderFs(),
            volumes=FakeVolumes([]),
            logger=self.logger,
            uid=uid,
            environ=self.env,
            top_trash_dir_rules_fs=RealTopTrashDirFs(),
        )

    def test_restore_one_file(self,  # type: Self
                              ):
        self.trash_dir.add_file_trashed_from_dir('foo-bar', self.cwd)
        assert sorted(self.root_dir.find_files_rel()) == [
            '/home/user/.local/share/Trash/files/foo-bar',
            '/home/user/.local/share/Trash/info/foo-bar.trashinfo',
        ]

        self.input.set_reply('0')
        self.cmd.run([])

        files_after_restore = sorted(self.root_dir.find_files_rel())
        assert (files_after_restore == ['/cwd/foo-bar'])
        assert '/home/user/.local/share/Trash/info/foo-bar.trashinfo' not in files_after_restore
        assert '/home/user/.local/share/Trash/files/foo-bar' not in files_after_restore

    def test_restore_file_with_parent(self,  # type: Self
                                      ):
        self.trash_dir.add_file_trashed_from_dir('foo', self.cwd / 'parent')
        assert sorted(self.root_dir.find_files_rel()) == [
            '/home/user/.local/share/Trash/files/foo',
            '/home/user/.local/share/Trash/info/foo.trashinfo',
        ]

        self.input.set_reply('0')
        self.cmd.run(['trash-restore'])

        # assert it has been restored
        assert self.root_dir.exists('/cwd/parent/foo')
        # assert that trashinfo is gone
        assert not self.root_dir.exists(
            '/home/user/.local/share/Trash/info/foo.trashinfo')
        # assert that backup copy is no there
        assert not self.root_dir.exists(
            '/home/user/.local/share/Trash/files/foo')
        # assert noting more to check in root_dir
        assert sorted(self.root_dir.find_files_rel()) == ['/cwd/parent/foo']
        # assert no warnings
        assert self.logger.captured == []

    def test_restore_over_existing_file_will_obstruct_restoration(self,
                                                                  # type: Self
                                                                  ):
        """
        What happens when we cannot restore file because another file is the
        restore location.
        """
        self.trash_dir.add_file_trashed_from_dir('bar', self.cwd,
                                                 'to-be-restored')
        self.cwd.write_file('bar',
                            'obstructing file')  # put a file where the trashed one should be restored
        assert sorted(self.root_dir.find_files_rel()) == [
            '/cwd/bar',
            '/home/user/.local/share/Trash/files/bar',
            '/home/user/.local/share/Trash/info/bar.trashinfo',
        ]

        self.input.set_reply('0')
        r = capture_exit_code2(lambda: self.cmd.run(['trash-restore']))

        assert sorted(self.root_dir.find_files_rel()) == [
            '/cwd/bar',
            '/home/user/.local/share/Trash/files/bar',
            '/home/user/.local/share/Trash/info/bar.trashinfo',
        ]

        # assert it cannot be restored
        assert self.root_dir.read('cwd/bar') != 'to-be-restored'
        assert self.root_dir.read('cwd/bar') == 'obstructing file'
        # assert that trashinfo remains there
        assert self.root_dir.exists(
            '/home/user/.local/share/Trash/info/bar.trashinfo')
        # assert that backup copy remains there
        assert self.root_dir.exists('/home/user/.local/share/Trash/files/bar')
        # assert a warnings is passed
        assert self.stderr.getvalue() == 'Refusing to overwrite existing file "bar".\n'
        assert r.exit_code == 1

    def teardown_method(self):
        self.temp_dir.clean_up()
