import sys
from typing import TypeVar

import pytest
from six import StringIO

from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import make_temp_dir
from tests.support.fakes.fake_trash_dir import FakeTrashDir, \
    FakeTrashDirWithRoot
from tests.support.fs.sorting_listdir_fs import SortingListdirFs
from tests.test_restore.support.fake_read_cwd import FakeReadCwdFs
from tests.test_restore.support.recording_logger import RecordingLogger
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_list_files_in_dir import RealListdirFs
from tests.support.fakes.fake_volumes import FakeVolumesFs
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.fs.real.real_file_reader_fs import RealFileReaderFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_restore_writer_fs import RealRestoreWriterFs
from trashcli.restore.restore_cmd import RestoreCmd

Self = TypeVar('Self', bound='TestRestoreListing')

@pytest.mark.slow
class TestRestoreListing:

    def setup_method(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.input = HardCodedInput()
        fs = RealFs()
        self.temp_dir = make_temp_dir(fs)

        self.root_dir = self.temp_dir
        self.support_fs = SupportFs(fs, self.root_dir)

        self.cwd = self.root_dir / "cwd"
        self.support_fs.mkdir_rel_p(self.cwd)

        self.home_dir = self.root_dir / "home/user"
        self.support_fs.mkdir_rel_p(self.home_dir)
        trash_dir_path = self.home_dir / ".local/share/Trash"
        self.support_fs.mkdir_rel_p(trash_dir_path)
        self.trash_dir = FakeTrashDirWithRoot(
            FakeTrashDir(trash_dir_path), self.root_dir
        )

        uid = 1000
        self.env = {'HOME': self.home_dir}
        # end of unix-like env

        self.cur_dir = FakeReadCwdFs(self.cwd)

        self.logger = RecordingLogger()
        self.cmd = RestoreCmd(
            stdout=self.stdout,
            stderr=self.stderr,
            exit=sys.exit,
            input=self.input,
            version="0.0.0",
            listing_fs=SortingListdirFs(RealListdirFs()),
            read_fs=RealPathReaderFs(),
            write_fs=RealRestoreWriterFs(),
            read_cwd=self.cur_dir,
            file_reader=RealFileReaderFs(),
            volumes=FakeVolumesFs([]),
            logger=self.logger,
            uid=uid,
            environ=self.env,
            top_trash_dir_rules_fs=RealFs(),
        )

    def teardown_method(self):
        self.temp_dir.clean_up()

    def test_with_no_args_should_show_only_files_in_cwd(
            self,  # type: Self
    ):
        cwd = self.root_dir / 'cwd'
        self.support_fs.mkdir_rel_p(cwd)
        self.trash_dir.add_trashed_file("cwd/file1")
        self.trash_dir.add_trashed_file("cwd/file2")
        self.trash_dir.add_trashed_file("cwd/file3")
        self.trash_dir.add_trashed_file("another_dir/fileA")
        self.trash_dir.add_trashed_file("another_dir/fileB")
        self.trash_dir.add_trashed_file("another_dir/fileC")

        self.cur_dir.chdir(cwd)
        self.input.set_reply('')
        self.cmd.run([])

        output = self.root_dir.clean_stream(self.stdout)
        # file from another dir are not listed
        assert 'fileA' not in output
        assert 'fileB' not in output
        assert 'fileC' not in output
        # only files from the cwd are listed
        assert (output ==
                '   0 2001-01-01 00:00:00 /cwd/file1\n'
                '   1 2001-01-01 00:00:00 /cwd/file2\n'
                '   2 2001-01-01 00:00:00 /cwd/file3\n'
                'No files were restored\n')

    def test_with_a_specific_path_as_arg_should_show_only_the_file_with_specific_path(
            self,  # type: Self
    ):
        root = self.root_dir
        cwd = self.root_dir / 'cwd'
        self.support_fs.mkdir_rel_p(cwd)
        self.trash_dir.add_trashed_file("/cwd/file1")
        self.trash_dir.add_trashed_file("/cwd/file2")
        self.trash_dir.add_trashed_file("/another/specific")

        self.cur_dir.chdir(cwd)
        self.input.set_reply('')
        self.cmd.run(['--sort=path', root / 'another'])

        output = self.root_dir.clean_stream(self.stdout)
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

        output = self.root_dir.clean_stream(self.stdout)
        # only files from the cwd are listed
        assert (output ==
                '   0 2001-01-01 00:00:00 /prefix\n'
                'No files were restored\n')

