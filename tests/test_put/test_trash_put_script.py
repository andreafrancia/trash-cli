import os
import unittest

import pytest

from tests.run_command import run_command
from tests.support.files import make_file
from tests.support.my_path import MyPath


@pytest.mark.slow
class TestPutScripts(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_trash_put_works(self):
        result = run_command('.', 'trash-put')
        assert ("usage: trash-put [OPTION]... FILE..." in
                result.stderr.splitlines())

    def test_trash_put_touch_filesystem(self):
        result = run_command('.', 'trash-put', ['non-existent'])
        assert (result.stderr ==
                "trash-put: cannot trash non existent 'non-existent'\n")

    def test_trashing_danglig_symlink_bug(self):
        os.symlink('non-existent', self.tmp_dir / 'dangling-link')

        result = run_command(self.tmp_dir, 'trash-put', ['dangling-link'])

        assert (result.stderr ==
                "trash-put: cannot trash symbolic link 'dangling-link'\n")
        assert os.path.lexists(self.tmp_dir / 'dangling-link')

    def test_trashing_normal_symlink(self):
        make_file(self.tmp_dir / 'link-target')
        os.symlink('link-target', self.tmp_dir / 'normal-link')

        result = run_command(self.tmp_dir, 'trash-put',
                             ['-v',
                              'normal-link',
                              '--trash-dir', self.tmp_dir / 'trash-dir',
                              ])

        assert ("trash-put: 'normal-link' trashed in %s" % (self.tmp_dir / 'trash-dir')
                in result.stderr.splitlines())
        assert (result.stdout.splitlines() == [])
        assert not os.path.lexists(self.tmp_dir / 'normal-link')
