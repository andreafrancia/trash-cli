from typing import TypeVar

import pytest

from tests.support.dirs.support_fs import SupportFs
from tests.support.dirs.temp_dir import make_temp_dir
from tests.support.fakes.fake_trash_dir import FakeTrashDir, \
    FakeTrashDirWithRoot
from tests.support.fs.sorting_listdir_fs import SortingListdirFs
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_list_files_in_dir import RealListdirFs
from tests.support.fakes.fake_volumes import FakeVolumesFs
from trashcli.restore.fs.real.real_file_reader_fs import RealFileReaderFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_restore_writer_fs import RealRestoreWriterFs

Self = TypeVar('Self', bound='TestRestoreListing')

@pytest.mark.slow
class TestRestoreListing:

    def setup_method(self):
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

        self.logger = RecordingLogger()
        self.user = RestoreUser(
            environ=self.env,
            uid=uid,
            file_reader=RealFileReaderFs(),
            path_read_fs=RealPathReaderFs(),
            write_fs=RealRestoreWriterFs(),
            listing_fs=SortingListdirFs(RealListdirFs()),
            version="0.0.0",
            volumes=FakeVolumesFs([]),
            logger=self.logger,
            top_trash_dir_rules_reader=RealFs(),
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

        res = self.user.run_restore(['trash-restore'], from_dir=cwd)

        output = self.root_dir.clean_str(res.stdout)
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

        res = self.user.run_restore(
            ['trash-restore', '--sort=path', root / 'another'],
            from_dir=cwd)

        output = self.root_dir.clean_str(res.stdout)
        # only files from the cwd are listed
        assert (output ==
                '   0 2001-01-01 00:00:00 /another/specific\n'
                'No files were restored\n')

    def test_path_prefix_bug_remain_fixed(self):
        root = self.root_dir
        self.trash_dir.add_trashed_file("/prefix")
        self.trash_dir.add_trashed_file("/prefix-with-other")

        res = self.user.run_restore(
            ['trash-restore', '--sort=path', root / 'prefix'],
            from_dir=self.cwd)

        output = self.root_dir.clean_str(res.stdout)
        # only files from the cwd are listed
        assert (output ==
                '   0 2001-01-01 00:00:00 /prefix\n'
                'No files were restored\n')
