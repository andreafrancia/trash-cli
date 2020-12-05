from nose.tools import assert_equal

from trashcli.restore import TrashDirectory


class TestTrashDir:
    def test_path(self):
        trash_dir = TrashDirectory('/Trash-501', '/')
        assert_equal('/Trash-501', trash_dir.path)
