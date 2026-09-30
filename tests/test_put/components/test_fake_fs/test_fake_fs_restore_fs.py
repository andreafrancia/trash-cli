import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.restore.fs.protocols.restore_fs import RestoreFs


@pytest.fixture
def fs():
    return FakeFs()


class TestFakeFsAsARestoreFs:
    def test_is_a_restore_fs(self, fs):
        restore_fs = fs  # type: RestoreFs

        assert restore_fs is fs

    def test_list_files_in_dir_returns_full_paths(self, fs):
        fs.make_file_and_dirs('/dir/a', '')
        fs.make_file_and_dirs('/dir/b', '')

        assert sorted(fs.list_files_in_dir('/dir')) == ['/dir/a', '/dir/b']

    def test_contents_of_decodes_bytes(self, fs):
        fs.make_file_and_dirs('/dir/a', b'contents')

        assert fs.contents_of('/dir/a') == 'contents'

    def test_path_lexists_does_not_follow_symlinks(self, fs):
        fs.symlink('/missing', '/link')

        assert fs.path_exists('/link') is False
        assert fs.path_lexists('/link') is True

    def test_path_isdir(self, fs):
        fs.make_file_and_dirs('/dir/a', '')

        assert fs.path_isdir('/dir') is True
        assert fs.path_isdir('/dir/a') is False

    def test_mkdirs(self, fs):
        fs.mkdirs('/a/b/c')

        assert fs.isdir('/a/b/c') is True

    def test_getcwd_as_realpath(self, fs):
        fs.cd('/some/dir')

        assert fs.getcwd_as_realpath() == '/some/dir'

    def test_list_mount_points(self, fs):
        fs.add_volume('/mnt')

        assert list(fs.list_mount_points()) == ['/mnt']
        assert fs.volume_of('/mnt/dir/file') == '/mnt'
