import pytest
from tests.support.py2mock import Mock, call

from tests.support.restore.fake_path_fs import FakePathFs
from trashcli.restore.trash_directories import TrashDirectories2


@pytest.mark.slow
class TestTrashDirectories2:
    def setup_method(self):
        self.trash_directories = Mock(spec=['all_trash_directories'])
        self.volumes = FakePathFs()
        self.volumes.add_volume('/')
        self.volumes.add_volume('/mnt')
        self.trash_directories2 = TrashDirectories2(
            self.volumes,
            self.trash_directories,
        )

    def test_when_user_dir_is_none(self):
        self.trash_directories.all_trash_directories.return_value = \
            "os-trash-directories"

        result = self.trash_directories2.trash_directories_or_user(None)

        assert self.trash_directories.mock_calls == [call.all_trash_directories()]
        assert 'os-trash-directories' == result

    def test_when_user_dir_is_specified(self):
        self.trash_directories.all_trash_directories.return_value = \
            "os-trash-directories"

        result = self.trash_directories2.trash_directories_or_user(
            '/mnt/user-trash_dir')

        assert self.trash_directories.mock_calls == []
        assert result == [('/mnt/user-trash_dir', '/mnt')]
