# Copyright (C) 2021 Andrea Francia Bereguardo(PV) Italy
import unittest

import pytest

from tests import run_command
from tests.run_command import last_line_of, first_line_of
from tests.support import MyPath
from textwrap import dedent


@pytest.mark.slow
class TestEndToEndPut(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()

    def test_last_line_of_help(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", ['--help'])

        assert last_line_of(result.stdout) == \
               'Report bugs to https://github.com/andreafrancia/trash-cli/issues'

    def test_without_args(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", [])

        assert [first_line_of(result.stderr),
                result.exit_code] == \
               ['Usage: trash-put [OPTION]... FILE...', 2]

    def test_wrong_option(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", ['--wrong-option'])

        assert [last_line_of(result.stderr),
                result.exit_code] == \
               ['trash-put: error: no such option: --wrong-option', 2]

    def test_on_help(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", ['--help'])

        assert [result.stdout,
                result.exit_code] == \
               [dedent('''\
            Usage: trash-put [OPTION]... FILE...

            Put files in trash

            Options:
              --version             show program's version number and exit
              -h, --help            show this help message and exit
              -d, --directory       ignored (for GNU rm compatibility)
              -f, --force           silently ignore nonexistent files
              -i, --interactive     prompt before every removal
              -r, -R, --recursive   ignored (for GNU rm compatibility)
              --trash-dir=TRASHDIR  use TRASHDIR as trash folder
              -v, --verbose         explain what is being done

            To remove a file whose name starts with a '-', for example '-foo',
            use one of these commands:

                trash -- -foo

                trash ./-foo

            Report bugs to https://github.com/andreafrancia/trash-cli/issues
            '''), 0]

    def test_it_should_skip_dot_entry(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", ['.'])

        assert [result.stderr, result.exit_code] == \
               ["trash-put: cannot trash directory '.'\n", 0]

    def test_it_should_skip_dotdot_entry(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", ['..'])

        assert [result.stderr, result.exit_code] == \
               ["trash-put: cannot trash directory '..'\n", 0]

    def test_it_should_print_usage_on_no_argument(self):
        result = run_command.run_command(self.tmp_dir, "trash-put", [])

        assert [result.stdout, result.stderr, result.exit_code] == \
               ['', 'Usage: trash-put [OPTION]... FILE...\n'
                    '\n'
                    'trash-put: error: Please specify the files to trash.\n', 2]

    def test_it_should_skip_missing_files(self):
        result = run_command.run_command(self.tmp_dir, "trash-put",
                                         ['-f', 'this_file_does_not_exist', 'nor_does_this_file'])

        assert [result.stdout, result.stderr, result.exit_code] == ['', '', 0]
