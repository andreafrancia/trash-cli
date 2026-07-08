import os

from tests.support.dirs.my_path import MyPath
from trashcli.fs import RealIsWorldWritable


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

    def teardown_method(self):
        self.tmp_dir.clean_up()
