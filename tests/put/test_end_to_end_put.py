import unittest

from tests import run_command
from tests.run_command import last_line_of
from tests.support import MyPath


class TestEndToEndPut(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", ['--help'])

        assert last_line_of(result.stdout) == \
               'Report bugs to https://github.com/andreafrancia/trash-cli/issues'
