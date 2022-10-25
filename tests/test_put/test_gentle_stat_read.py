import grp
import os
import pwd
import unittest

import six

from tests.support.files import make_file
from tests.support.my_path import MyPath
from trashcli.put.reporter import gentle_stat_read


class TestGentleStatRead(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_file_non_found(self):
        result = gentle_stat_read(self.tmp_dir / 'not-existent')

        six.assertRegex(
            self, result,
            r"\[Errno 2\] No such file or directory: '/.*/not-existent'")

    def test_file(self):
        make_file(self.tmp_dir / 'pippo.txt')
        os.chmod(self.tmp_dir / 'pippo.txt', 0o531)

        result = gentle_stat_read(self.tmp_dir / 'pippo.txt')

        assert result == '531 %s %s' % (
            self.current_user(), self.current_group()
        )

    def tearDown(self):
        self.tmp_dir.clean_up()

    @staticmethod
    def current_user():
        return pwd.getpwuid(os.getuid()).pw_name

    @staticmethod
    def current_group():
        return grp.getgrgid(os.getgid()).gr_name
