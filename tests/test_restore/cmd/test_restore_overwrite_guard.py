import os

import pytest

from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import trashinfo_content_default_date
from tests.support.files import read_file
from tests.support.restore.restore_file_fixture import RestoreFileFixture
from tests.support.restore.restore_user import RestoreUser
from tests.test_restore.support.recording_logger import RecordingLogger
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fslib.real.real_list_files_in_dir import RealListFilesInDir
from trashcli.fstab.volumes import FakeVolumes
from trashcli.fslib.real.real_fs import RealFs
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs
from trashcli.restore.fs.real.real_file_reader_fs import RealFileReaderFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_restore_writer_fs import RealRestoreWriterFs
from trashcli.restore.fs.real.real_restore_read_fs import RealRestoreReadFs


@pytest.mark.slow
class TestRestoreOverwriteGuard:
    def setup_method(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.fixture = RestoreFileFixture(self.tmp_dir / 'XDG_DATA_HOME',
                                          RealFs())
        self.cwd = self.tmp_dir / 'cwd'
        os.makedirs(self.cwd)
        self.user = RestoreUser(
            environ={'XDG_DATA_HOME': self.tmp_dir / 'XDG_DATA_HOME'},
            uid=os.getuid(),
            file_reader=RealFileReaderFs(),
            path_read_fs=RealPathReaderFs(),
            read_fs=RealRestoreReadFs(),
            write_fs=RealRestoreWriterFs(),
            listing_fs=RealListFilesInDir(),
            version='0.0.0',
            volumes=FakeVolumes([]),
            volume_path_fs=RealVolumePathFs(),
            top_trash_dir_rules_reader=RealTopTrashDirFs(),
            logger=RecordingLogger())

    def test_it_refuses_to_restore_over_a_dangling_symlink(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        os.symlink(self.cwd / 'this-target-does-not-exist', self.cwd / 'foo')

        res = self.user.run_restore(reply='0', from_dir=self.cwd)

        assert res.stderr == 'Refusing to overwrite existing file "foo".\n'

    def test_it_refuses_to_restore_onto_a_directory_even_with_overwrite(self):
        self.fixture.having_a_trashed_file(self.cwd / 'foo')
        os.makedirs(self.cwd / 'foo')

        res = self.user.run_restore(args=['trash-restore', '--overwrite'],
                                    reply='0', from_dir=self.cwd)

        assert res.stderr == 'Refusing to overwrite existing file "foo".\n'

    def teardown_method(self):
        self.tmp_dir.clean_up()

    def test_batch_keeps_conflicting_entry_and_restores_the_next_file(self):
        trash = self.tmp_dir / 'XDG_DATA_HOME/Trash'
        for name in ['a', 'b']:
            self.fixture.make_file(trash / ('info/' + name + '.trashinfo'),
                                   trashinfo_content_default_date(self.cwd / name))
            self.fixture.make_file(trash / ('files/' + name), 'trashed ' + name)
        self.fixture.make_file(self.cwd / 'a', 'existing a')

        res = self.user.run_restore(args=['trash-restore', '--sort=path'],
                                    reply='0-1', from_dir=self.cwd)

        assert res.exit_code == 1
        assert res.stderr == 'Refusing to overwrite existing file "a".\n'
        assert read_file(self.cwd / 'a') == 'existing a'
        assert read_file(self.cwd / 'b') == 'trashed b'
        assert read_file(trash / 'files/a') == 'trashed a'
        assert os.path.exists(trash / 'info/a.trashinfo')
        assert not os.path.exists(trash / 'files/b')
        assert not os.path.exists(trash / 'info/b.trashinfo')
