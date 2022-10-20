import unittest

from tests.test_put.support.fake_fs.fake_fs import FakeFs
from trashcli.put.ensure_dir import EnsureDir


class TestEnsureDir(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs('/')
        self.ensure_dir = EnsureDir(self.fs)

    def test_happy_path(self):
        self.ensure_dir.ensure_dir('/foo', 0o755)

        assert [self.fs.isdir('/foo'),
                self.fs.get_mod_s('/foo')] == [True, '0o755']

    def test_makedirs_honor_permissions(self):
        self.fs.makedirs('/foo', 0o000)

        assert [self.fs.get_mod_s('/foo')] == ['0o000']

    def test_bug_when_no_permissions_it_overrides_the_permissions(self):
        self.fs.makedirs('/foo', 0o000)
        self.ensure_dir.ensure_dir('/foo', 0o755)

        assert [self.fs.isdir('/foo'),
                self.fs.get_mod_s('/foo')] == [True, '0o755']
