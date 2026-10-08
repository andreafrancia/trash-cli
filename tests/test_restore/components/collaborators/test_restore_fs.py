from tests.support.list_abstract_methods import list_abstract_methods
from trashcli.restore.fs.protocols.restore_fs import RestoreFs


class TestRestoreFs:
    def test(self):
        assert list_abstract_methods(RestoreFs) == {
            'getcwd_as_realpath',
            'list_mount_points',
            'listdir',
            'mkdirs',
            'move',
            'path_exists',
            'path_isdir',
            'path_lexists',
            'read_file',
            'remove_file',
            'volume_of'
        }