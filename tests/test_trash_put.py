# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy
import unittest

from trashcli.put import TrashPutCmd

from six import StringIO
from .asserts import assert_equals_with_unidiff
from textwrap import dedent


class TrashPutTest(unittest.TestCase):
    def run_trash_put(self, *arg):
        self.stderr = StringIO()
        self.stdout = StringIO()
        args = ['trash-put'] + list(arg)
        cmd = TrashPutCmd(self.stdout,
                          self.stderr,
                          None,
                          None,
                          None,
                          None,
                          None,
                          None,
                          None)
        self._collect_exit_code(lambda:cmd.run(args))

    def _collect_exit_code(self, main_function):
        self.exit_code = 0
        result=main_function()
        if result is not None:
            self.exit_code=result

    def stderr_should_be(self, expected_err):
        assert_equals_with_unidiff(expected_err, self._actual_stderr())

    def stdout_should_be(self, expected_out):
        assert_equals_with_unidiff(expected_out, self._actual_stdout())

    def _actual_stderr(self):
        return self.stderr.getvalue()

    def _actual_stdout(self):
        return self.stdout.getvalue()

class TestWhenNoArgs(TrashPutTest):
    def setUp(self):
        self.run_trash_put()

    def test_should_report_usage(self):
        assert_line_in_text('Usage: trash-put [OPTION]... FILE...',
                            self.stderr.getvalue())
    def test_exit_code_should_be_not_zero(self):
        assert 2 == self.exit_code

class TestTrashPutWithWrongOption(TrashPutTest):
    def test_something(self):
        self.run_trash_put('--wrong-option')
        self.stderr_should_be(dedent('''\
            Usage: trash-put [OPTION]... FILE...

            trash-put: error: no such option: --wrong-option
            '''))
        self.stdout_should_be('')
        assert 2 == self.exit_code

def assert_line_in_text(expected_line, text):
    assert expected_line in text.splitlines(), (
                'Line not found in text\n'
                'line: %s\n' % expected_line +
                'text:\n%s\n' % format(text.splitlines()))


class TestTrashPutCmd(TrashPutTest):

    def test_on_help_option_print_help(self):
        self.run_trash_put('--help')
        self.stdout_should_be(dedent('''\
            Usage: trash-put [OPTION]... FILE...

            Put files in trash

            Options:
              --version             show program's version number and exit
              -h, --help            show this help message and exit
              -d, --directory       ignored (for GNU rm compatibility)
              -f, --force           silently ignore nonexistent files
              -i, --interactive     ignored (for GNU rm compatibility)
              -r, -R, --recursive   ignored (for GNU rm compatibility)
              --trash-dir=TRASHDIR  use TRASHDIR as trash folder
              -v, --verbose         explain what is being done

            To remove a file whose name starts with a '-', for example '-foo',
            use one of these commands:

                trash -- -foo

                trash ./-foo

            Report bugs to https://github.com/andreafrancia/trash-cli/issues
            '''))

    def test_it_should_skip_dot_entry(self):
        self.run_trash_put('.')
        self.stderr_should_be("trash-put: cannot trash directory '.'\n")

    def test_it_should_skip_dotdot_entry(self):
        self.run_trash_put('..')
        self.stderr_should_be("trash-put: cannot trash directory '..'\n")

    def test_it_should_print_usage_on_no_argument(self):
        self.run_trash_put()
        self.stderr_should_be(
            'Usage: trash-put [OPTION]... FILE...\n'
            '\n'
            'trash-put: error: Please specify the files to trash.\n')
        self.stdout_should_be('')

    def test_it_should_skip_missing_files(self):
        self.run_trash_put('-f', 'this_file_does_not_exist', 'nor_does_this_file')
        self.stderr_should_be('')
        self.stdout_should_be('')
