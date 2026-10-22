import unittest

import pytest

from tests.support.capture_error import capture_error
from tests.support.dirs.temp_dir import make_temp_dir
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class TestRealFsPermissions(unittest.TestCase):
    def setUp(self):
        self.fs = RealFs()
        self.tmp_dir = make_temp_dir(self.fs)

    def test(self):
        self.fs.makedirs(self.tmp_dir / 'dir', 0o000)
        error = capture_error(
            lambda: self.fs.write_file(self.tmp_dir / 'dir' / 'file', 'content'))

        assert str(error) == "[Errno 13] Permission denied: '%s'" % (
                    self.tmp_dir / 'dir' / 'file')
        self.fs.chmod(self.tmp_dir / 'dir', 0o755)

    def test_chmod_and_get_mod(self):
        path = self.tmp_dir / 'file'
        self.fs.write_file(path, 'content')
        self.fs.chmod(path, 0o123)

        assert self.fs.get_mod(path) == 0o123

    def test_seems_to_have_delete_permissions_when_parent_is_writable_and_searchable(self):
        self.fs.write_file(self.tmp_dir / 'file', 'content')

        assert self.fs.seems_to_have_delete_permissions(self.tmp_dir / 'file') is True

    def test_seems_to_have_delete_permissions_when_parent_has_no_write_permission(self):
        self.fs.mkdir(self.tmp_dir / 'dir')
        self.fs.write_file(self.tmp_dir / 'dir' / 'file', 'content')
        self.fs.chmod(self.tmp_dir / 'dir', 0o500)

        try:
            assert self.fs.seems_to_have_delete_permissions(
                self.tmp_dir / 'dir' / 'file') is False
        finally:
            self.fs.chmod(self.tmp_dir / 'dir', 0o755)

    def test_seems_to_have_delete_permissions_when_parent_has_no_search_permission(self):
        self.fs.mkdir(self.tmp_dir / 'dir')
        self.fs.write_file(self.tmp_dir / 'dir' / 'file', 'content')
        self.fs.chmod(self.tmp_dir / 'dir', 0o600)

        try:
            assert self.fs.seems_to_have_delete_permissions(
                self.tmp_dir / 'dir' / 'file') is False
        finally:
            self.fs.chmod(self.tmp_dir / 'dir', 0o755)

    def tearDown(self):
        self.tmp_dir.clean_up()
