import unittest

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.put.format_mode import format_mode
from trashcli.put.dir_maker import DirMaker


class TestEnsureDir(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs('/')
        self.dir_maker = DirMaker(self.fs)

    def test_happy_path(self):
        self.dir_maker.mkdir_p('/foo', 0o755)

        assert [self.fs.isdir('/foo'),
                format_mode(self.fs.get_mod('/foo'))] == [True, '0o755']

    def test_makedirs_honor_permissions(self):
        self.fs.makedirs('/foo', 0o000)

        assert [format_mode(self.fs.get_mod('/foo'))] == ['0o000']

    def test_bug_when_no_permissions_it_overrides_the_permissions(self):
        self.fs.makedirs('/foo', 0o000)
        self.dir_maker.mkdir_p('/foo', 0o755)

        assert [self.fs.isdir('/foo'),
                format_mode(self.fs.get_mod('/foo'))] == [True, '0o000']
