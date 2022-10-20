import unittest

from tests.support.capture_error import capture_error
from tests.support.my_path import MyPath
from trashcli.put.real_fs import RealFs


class TestRealFsPermissions(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        self.fs.makedirs(self.tmp_dir / 'dir', 0o000)
        error = capture_error(
            lambda: self.fs.make_file(self.tmp_dir / 'dir' / 'file', 'content'))

        assert str(error) == "[Errno 13] Permission denied: '%s'" % (
                    self.tmp_dir / 'dir' / 'file')
        self.fs.chmod(self.tmp_dir / 'dir', 0o755)

    def test_chmod_and_get_mod(self):
        path = self.tmp_dir / 'file'
        self.fs.make_file(path, 'content')
        self.fs.chmod(path, 0o123)

        assert self.fs.get_mod(path) == 0o123

    def tearDown(self):
        self.tmp_dir.clean_up()
