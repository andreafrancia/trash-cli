import unittest

import pytest

from ..support import MyPath
from .. import run_command


@pytest.mark.slow
class TestEndToEndRestore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_no_file_trashed(self):
        result = run_command.run_command(self.tmp_dir, "trash-list", ['--help'])

        self.assertEqual("""\
usage: trash-list [-h] [--version] [--trash-dir TRASH_DIRS]

List trashed files

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --trash-dir TRASH_DIRS
                        specify the trash directory to use

Report bugs to https://github.com/andreafrancia/trash-cli/issues
""", result.stdout)

    def tearDown(self):
        self.tmp_dir.clean_up()
