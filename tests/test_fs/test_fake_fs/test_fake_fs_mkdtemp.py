import errno
import os

import pytest

from tests.support.put.fake_fs.fake_fs import FakeFs
from trashcli.compat import octal


class TestFakeFsMkdtemp:
    def setup_method(self):
        self.fs = FakeFs()

    def test_mkdtemp__will_always_return_different_values(self):
        first = self.fs.mkdtemp()
        second = self.fs.mkdtemp()

        assert first != second

    def test_mkdtemp__will_add_suffix_if_specified(self):
        result = self.fs.mkdtemp(suffix='.suffix')

        basename = os.path.basename(result)
        assert basename[-len(".suffix"):] == '.suffix'

    def test_mkdtemp__will_add_prefix_if_specified(self):
        result = self.fs.mkdtemp(prefix='myprefix-')

        basename = os.path.basename(result)
        assert basename[0:len("myprefix-")] == "myprefix-"

    def test_mkdtemp__default_prefix(self):
        result = self.fs.mkdtemp()

        basename = os.path.basename(result)
        assert basename[0:len("tmp")] == "tmp"

    def test_mkdtemp__will_place_temp_dir_in_the_system_tmp_dir(self):
        result = self.fs.mkdtemp()

        dirname = os.path.dirname(result)
        assert dirname == self.fs.gettempdir()

    def test_mkdtemp__will_place_temp_dir_in_dir_if_specified(self):
        test_temp_dir = self.fs.mkdtemp()
        result = self.fs.mkdtemp(dir=test_temp_dir)

        dirname = os.path.dirname(result)
        assert dirname == test_temp_dir
        assert dirname != self.fs.gettempdir()

    def test_mkdtemp__with_suffix_prefix_and_dir(self):
        test_temp_dir = self.fs.mkdtemp()

        result = self.fs.mkdtemp(suffix='.suffix', prefix='myprefix-',
                                 dir=test_temp_dir)

        import re
        pattern = ("^" + re.escape(test_temp_dir) + os.sep +
                   "myprefix-.*.suffix$")
        assert re.match(pattern, result)

    def test_mkdtemp__creates_a_dir(self):
        result = self.fs.mkdtemp()

        assert self.fs.path_isdir(result)

    def test_mkdtemp__creates_a_dir_with_permission_700(self):
        result = self.fs.mkdtemp()

        assert octal(self.fs.get_mod(result)) == '0o700'

    def test_mkdtemp__fails_if_the_given_dir_does_not_exist(self):
        with pytest.raises(OSError) as excinfo:
            self.fs.mkdtemp(dir='/missing')

        assert excinfo.value.errno == errno.ENOENT
        assert str(excinfo.value).startswith(
            "[Errno 2] No such file or directory: '/missing/tmp")
