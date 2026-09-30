import os

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real.real_is_world_writable import RealIsWorldWritable


class TestRealIsWorldWritable:
    # focused integration test: exercises only is_world_writable on the real fs
    def setup_method(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.checker = RealIsWorldWritable()

    def test_a_private_dir_is_not_world_writable(self):
        os.chmod(self.tmp_dir, 0o700)

        assert self.checker.is_world_writable(self.tmp_dir) is False

    def test_a_world_writable_dir_is_detected(self):
        os.chmod(self.tmp_dir, 0o777)

        assert self.checker.is_world_writable(self.tmp_dir) is True

    def test_a_missing_path_is_not_world_writable(self):
        assert self.checker.is_world_writable(self.tmp_dir / 'nope') is False

    def test_a_symlink_to_a_private_dir_is_not_world_writable(self):
        os.mkdir(self.tmp_dir / 'dir', 0o700)
        os.symlink(self.tmp_dir / 'dir', self.tmp_dir / 'link')

        assert self.checker.is_world_writable(self.tmp_dir / 'link') is False

    def test_a_symlink_to_a_world_writable_dir_is_detected(self):
        os.mkdir(self.tmp_dir / 'dir')
        os.chmod(self.tmp_dir / 'dir', 0o777)
        os.symlink(self.tmp_dir / 'dir', self.tmp_dir / 'link')

        assert self.checker.is_world_writable(self.tmp_dir / 'link') is True

    def test_a_dangling_symlink_is_not_world_writable(self):
        os.symlink(self.tmp_dir / 'none', self.tmp_dir / 'link')

        assert self.checker.is_world_writable(self.tmp_dir / 'link') is False

    def teardown_method(self):
        self.tmp_dir.clean_up()
