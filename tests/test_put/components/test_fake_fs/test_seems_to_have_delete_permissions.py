from tests.support.put.fake_fs.fake_fs import FakeFs


class TestSeemsToHaveDeletePermissions:
    def setup_method(self):
        self.fs = FakeFs()

    def test_true_when_parent_is_writable(self):
        self.fs.makedirs("/dir", 0o755)
        self.fs.make_file("/dir/file", "content")

        assert self.fs.seems_to_have_delete_permissions("/dir/file") is True

    def test_false_when_parent_is_not_writable(self):
        self.fs.makedirs("/dir", 0o755)
        self.fs.make_file("/dir/file", "content")
        self.fs.chmod("/dir", 0o500)

        assert self.fs.seems_to_have_delete_permissions("/dir/file") is False

    def test_true_for_a_file_directly_under_root_with_default_mode(self):
        # exercises the `parent == '/'` branch: the root inode has no
        # parent directory entry of its own, so its mode cannot be looked
        # up via the normal get_mod() traversal.
        self.fs.make_file("/file", "content")

        assert self.fs.seems_to_have_delete_permissions("/file") is True

    def test_false_for_a_file_directly_under_root_without_write_permission(self):
        self.fs.make_file("/file", "content")
        self.fs.root_inode.chmod(0o500)

        assert self.fs.seems_to_have_delete_permissions("/file") is False
