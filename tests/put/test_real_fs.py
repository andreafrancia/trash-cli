import unittest

from tests.support.capture_error import capture_error
from tests.support.my_path import MyPath
from trashcli.put.real_fs import RealFs


class TestRealFs(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        self.fs.makedirs(self.tmp_dir / 'dir', 0o000)
        error = capture_error(
            lambda: self.fs.make_file(self.tmp_dir / 'dir' / 'file', 'content'))

        assert str(error) == "[Errno 13] Permission denied: '%s'" % (
                    self.tmp_dir / 'dir' / 'file')

    def tearDown(self):
        self.fs.chmod(self.tmp_dir / 'dir', 0o755)
        self.tmp_dir.clean_up()
