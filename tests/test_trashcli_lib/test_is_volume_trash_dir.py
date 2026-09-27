from trashcli.lib.trash_dirs import is_volume_trash_dir


class TestIsVolumeTrashDir:
    def test_per_user_volume_trash(self):
        assert is_volume_trash_dir('/mnt/.Trash-123', '/mnt') is True

    def test_shared_volume_trash(self):
        assert is_volume_trash_dir('/mnt/.Trash/123', '/mnt') is True

    def test_trailing_slash(self):
        assert is_volume_trash_dir('/mnt/.Trash-123/', '/mnt/') is True

    def test_volume_trash_of_the_root_volume(self):
        assert is_volume_trash_dir('/.Trash-123', '/') is True

    def test_home_trash(self):
        assert is_volume_trash_dir('/home/user/.local/share/Trash',
                                   '/home') is False

    def test_trash_dir_not_directly_under_the_volume(self):
        assert is_volume_trash_dir('/tmp/xyz/trash-dir', '/tmp') is False

    def test_volume_trash_like_dir_not_at_the_top_of_the_volume(self):
        assert is_volume_trash_dir('/mnt/sub/.Trash-123', '/mnt') is False
