import sys
from typing import TypeVar

from six import StringIO

from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import FakeTrashDir, \
    FakeTrashDirWithRoot
from tests.support.py2mock import Mock
from tests.test_restore.support.capture_logger import CaptureLogger
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fstab.volumes import FakeVolumes
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.real_restore_fs import RealRestoreWriterFs, \
    RealRestoreReaderFs, RealFileReaderFs, \
    RealListingFs
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
        self.trash_dir = FakeTrashDirWithRoot(
            self.setup_trash_dir(self.home_dir), self.root_dir
        )

        uid = 1000
        self.env = {'HOME': self.home_dir}
        # end of unix-like env

        self.cur_dir = FakeReadCwdFs(self.cwd)

        self.logger = CaptureLogger()
        self.trashed_files = Mock(spec=TrashedFiles)
        self.cmd = RestoreCmd(
            stdout=self.stdout,
            stderr=self.stderr,
            exit=sys.exit,
            input=self.input,
            version="0.0.0",
            listing_fs=RealListingFs(),
            read_fs=RealRestoreReaderFs(),
            write_fs=RealRestoreWriterFs(),
            read_cwd=self.cur_dir,
            file_reader=RealFileReaderFs(),
            volumes=FakeVolumes([]),
            logger=self.logger,
            uid=uid,
            environ=self.env,
            top_trash_dir_rules_fs=RealTopTrashDirFs(),
        )

    def teardown_method(self):
        self.temp_dir.clean_up()

    def test_with_no_args_should_show_only_files_in_cwd(
            self,  # type: Self
    ):
        cwd = self.root_dir / 'cwd'
        self.trash_dir.add_trashed_file("cwd/file1")
        self.trash_dir.add_trashed_file("cwd/file2")
        self.trash_dir.add_trashed_file("cwd/file3")
        self.trash_dir.add_trashed_file("another_dir/fileA")
        self.trash_dir.add_trashed_file("another_dir/fileB")
        self.trash_dir.add_trashed_file("another_dir/fileC")

        self.cur_dir.chdir(cwd.mkdirs())
        self.input.set_reply('')
        self.cmd.run([])

        output = self.root_dir.clean_str(self.stdout)
        # file from another dir are not listed
        assert 'fileA' not in output
        assert 'fileB' not in output
        assert 'fileC' not in output
        # only files from the cwd are listed
        assert (output ==
                '   0 2001-01-01 00:00:00 /cwd/file2\n'
                '   1 2001-01-01 00:00:00 /cwd/file3\n'
                '   2 2001-01-01 00:00:00 /cwd/file1\n'
                'No files were restored\n')

    def test_with_a_specific_path_as_arg_should_show_only_the_file_with_specific_path(
            self,  # type: Self
    ):
        root = self.root_dir
        cwd = self.root_dir / 'cwd'
        self.trash_dir.add_trashed_file("/cwd/file1")
        self.trash_dir.add_trashed_file("/cwd/file2")
        self.trash_dir.add_trashed_file("/another/specific")

        self.cur_dir.chdir(cwd.mkdirs())
        self.input.set_reply('')
        self.cmd.run(['--sort=path', root / 'another'])

        output = self.root_dir.clean_str(self.stdout)
        # only files from the cwd are listed
        assert (output ==
                '   0 2001-01-01 00:00:00 /another/specific\n'
                'No files were restored\n')

    def test_path_prefix_bug_remain_fixed(self):
        root = self.root_dir
        self.trash_dir.add_trashed_file("/prefix")
        self.trash_dir.add_trashed_file("/prefix-with-other")

        self.input.set_reply('')
        self.cmd.run(['--sort=path', root / 'prefix'])

        output = self.root_dir.clean_str(self.stdout)
        # only files from the cwd are listed
        assert (output ==
                '   0 2001-01-01 00:00:00 /prefix\n'
                'No files were restored\n')

