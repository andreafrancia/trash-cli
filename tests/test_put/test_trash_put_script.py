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

    def test_trashes_dangling_symlink(self):
        self.make_dangling_link(self.tmp_dir / 'link')

        result = run_command(self.tmp_dir, 'trash-put', [
            'link',
            '--trash-dir', self.tmp_dir / 'trash-dir',
        ])

        assert (result.stdout, result.stderr == "", "")
        assert not os.path.lexists(self.tmp_dir / 'link')
        assert os.path.lexists(self.tmp_dir / 'trash-dir' / 'files' / 'link')

    def test_trashes_connected_symlink(self):
        self.make_connected_link(self.tmp_dir / 'link')

        result = run_command(self.tmp_dir, 'trash-put', [
            'link',
            '--trash-dir', self.tmp_dir / 'trash-dir',
        ])

        assert (result.stdout, result.stderr == "", "")
        assert not os.path.lexists(self.tmp_dir / 'link')
        assert os.path.lexists(self.tmp_dir / 'trash-dir' / 'files' / 'link')

    def make_connected_link(self, path):
        make_file(self.tmp_dir / 'link-target')
        os.symlink('link-target', path)

    def make_dangling_link(self, path):
        os.symlink('non-existent', self.tmp_dir / 'link')

    def tearDown(self):
        self.tmp_dir.clean_up()
