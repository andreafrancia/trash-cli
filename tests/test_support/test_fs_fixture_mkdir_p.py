import pytest

from tests.support.files import FsFixture
from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.compat import octal


class TestFsFixtureMkdirP:
    @pytest.fixture
    def fs(self):
        return FakeFs()

    @pytest.fixture
    def fsx(self, fs):
        return FsFixture(fs)

    def test_mkdir_p_will_create_dir(self, fs, fsx):
        fsx.mkdir_p('test')
        assert fs.path_isdir('test') == True

    def test_mkdir_p_will_use_the_default_mode(self, fs, fsx):
        fsx.mkdir_p('test')
        assert octal(fs.get_mod('test')) == '0o777'

    def test_mkdir_p_will_accept_dir_already_exist(self, fs, fsx):
        fsx.mkdir_p('test')
        fsx.mkdir_p('test')
        assert fs.path_isdir('test') == True
