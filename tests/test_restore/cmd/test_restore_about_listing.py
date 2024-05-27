from typing import List

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.restore.fs.fake_restore_fs import FakeRestoreFs
from tests.support.trash_dirs.trash_dir_fixture import TrashDirFixture
from tests.support.restore.restore_user import RestoreUser
from tests.support.run.cmd_result import CmdResult
from trashcli.fstab.volumes import FakeVolumes
from trashcli.lib.trash_dirs import home_trash_dir_path_from_env


class TestRestorCmdAboutListing:
    def setup_method(self):
        self.fs = FakeFs()
        self.restore_fs = FakeRestoreFs(self.fs)
        self.volumes = FakeVolumes([])
        environ = {'HOME': '/home/user'}
        self.user = RestoreUser(environ=environ,
                                uid=123,
                                version='1.0',
                                volumes=self.volumes,
                                restore_fs=self.fs,
                                fs=self.fs,
                                cwd="/dir",
                                reply='')
        trash_dir_path = home_trash_dir_path_from_env(environ)[0]
        self.trash_dir = TrashDirFixture(self.restore_fs.fs,
                                         trash_dir_path)

    def test_with_no_args_and_files_in_trashcan(self):
        self.trash_dir.add_trashed_file('/dir/location')
        self.trash_dir.add_trashed_file('/dir/location')
        self.trash_dir.add_trashed_file('/specific/path')

        result = self.user.run_restore(['trash-restore'])

        assert extract_trashed_files(result) == [
            '/dir/location',
            '/dir/location'
        ]

    def test_with_no_args_and_files_in_trashcan_2(self):
        self.trash_dir.add_trashed_file('/dir/location')
        self.trash_dir.add_trashed_file('/dir/location')
        self.trash_dir.add_trashed_file('/specific/path')

        result = self.user.run_restore(['trash-restore', '/specific/path'])

        assert extract_trashed_files(result) == ['/specific/path']

    def test_with_with_path_prefix_bug(self):
        self.trash_dir.add_trashed_file('/prefix'),
        self.trash_dir.add_trashed_file('/prefix-with-other')

        result = self.user.run_restore(['trash-restore', '/prefix'])

        assert extract_trashed_files(result) == ['/prefix']

    def run_restore(self, args, reply='', from_dir=None):
        return self.user.run_restore(args, reply, from_dir)

    def add_file_trashed_at(self, original_location, deletion_date):
        self.fs.make_trashed_file(original_location, '/home/user/.local/share/Trash',
                                  deletion_date, '')

def extract_trashed_files(result,  # type: CmdResult
                          ):  # type: (...) -> List[str]
    if result.stderr != '':
        raise AssertionError("stderr should not be empty: " +
                             repr(result.stderr))
    a = result.output()
    a = a.split("\n")
    a = [l for l in a if l != ""]
    a = [l for l in a if l != "No files were restored"]
    a = [l.replace('1970-01-01 00:00:00', '') for l in a]
    a = [l[6:] for l in a]
    return a

