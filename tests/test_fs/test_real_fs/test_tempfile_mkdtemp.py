import errno
import os
import tempfile

import pytest

from trashcli.compat import octal
from trashcli.fslib.real.real_fs import RealFs


@pytest.mark.slow
class TestTempfileMkdTemp:
    def setup_method(self):
        self.fs = RealFs()

    def test_mkdtemp__will_always_return_different_values(self):
        first = tempfile.mkdtemp()
        second = tempfile.mkdtemp()

        assert first != second

    def test_mkdtemp__will_add_suffix_if_specified(self):
        result = tempfile.mkdtemp(suffix='.suffix')

        basename = os.path.basename(result)
        assert basename[-len(".suffix"):] == '.suffix'

    def test_mkdtemp__will_add_prefix_if_specified(self):
        result = tempfile.mkdtemp(prefix='myprefix-')

        basename = os.path.basename(result)
        assert basename[0:len("myprefix-")] == "myprefix-"

    def test_mkdtemp__will_place_temp_dir_in_the_system_tmp_dir(self):
        result = tempfile.mkdtemp()

        dirname = os.path.dirname(result)
        assert dirname == tempfile.gettempdir()

    def test_mkdtemp__will_place_temp_dir_in_dir_if_specified(self):
        test_temp_dir = tempfile.mkdtemp()
        result = tempfile.mkdtemp(dir=test_temp_dir)

        dirname = os.path.dirname(result)
        assert dirname == test_temp_dir
        assert dirname != tempfile.gettempdir()

    def test_mkdtemp__with_suffix_prefix_and_dir(self):
        test_temp_dir = tempfile.mkdtemp()

        result = tempfile.mkdtemp(suffix='.suffix', prefix='myprefix-',
                                  dir=test_temp_dir)

        import re
        pattern = ("^" + re.escape(test_temp_dir) + os.sep +
                   "myprefix-.*.suffix$")
        assert re.match(pattern, result)

    def test_mkdtemp__creates_a_dir(self):
        result = tempfile.mkdtemp()

        assert self.fs.path_isdir(result)

    def test_mkdtemp__creates_a_dir_with_permission_700(self):
        result = tempfile.mkdtemp()

        assert octal(self.fs.get_mod(result)) == '0o700'

    def test_mkdtemp__fails_if_the_given_dir_does_not_exist(self):
        with pytest.raises(OSError) as excinfo:
            tempfile.mkdtemp(dir='/missing')

        assert excinfo.value.errno == errno.ENOENT
        assert str(excinfo.value).startswith(
            "[Errno 2] No such file or directory: '/missing/tmp")


