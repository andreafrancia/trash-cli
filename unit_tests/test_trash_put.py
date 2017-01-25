# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.put import TrashPutCmd
from trashcli.put import TopDirRelativePaths, AbsolutePaths
from trashcli.put import TopTrashDirWriteRules, all_is_ok_checker

from nose.tools import assert_in, assert_equals
from unit_tests.myStringIO import StringIO
from integration_tests.assert_equals_with_unidiff import assert_equals_with_unidiff
from textwrap import dedent
from mock import Mock, call

class TestTrashPutTrashDirectory:
    def setUp(self):
        parent_path = lambda _ : None
        volume_of = lambda _ : '/'
        self.try_trash_file_using_candidates = Mock()
        self.cmd = TrashPutCmd(None,
                               None,
                               {'XDG_DATA_HOME':'~/xdh'},
                               volume_of,
                               parent_path,
                               None,
                               None,
                               None,
                               None)
        self.cmd.getuid = lambda : '123'
        self.cmd.try_trash_file_using_candidates = self.try_trash_file_using_candidates

    def test_normally(self):

        self.cmd.run(['trash-put', 'file'])

        assert_equals([call('file', '/', [
            ('~/xdh/Trash', '/', AbsolutePaths, all_is_ok_checker),
            ('/.Trash/123', '/', TopDirRelativePaths, TopTrashDirWriteRules),
            ('/.Trash-123', '/', TopDirRelativePaths, all_is_ok_checker),
            ])], self.try_trash_file_using_candidates.mock_calls)

    def test_with_a_specified_trashdir(self):
        self.cmd.run(['trash-put', '--trash-dir=/Trash2', 'file'])

        assert_equals([call('file', '/', [
            ('/Trash2', '/', TopDirRelativePaths, all_is_ok_checker),
            ])], self.try_trash_file_using_candidates.mock_calls)


class TrashPutTest:
    def run(self, *arg):
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
        self.run()

    def test_should_report_usage(self):
        assert_line_in_text('Usage: trash-put [OPTION]... FILE...',
                            self.stderr.getvalue())
    def test_exit_code_should_be_not_zero(self):
        assert_equals(2, self.exit_code)

class TestTrashPutWithWrongOption(TrashPutTest):
    def test_something(self):
        self.run('--wrong-option')
        self.stderr_should_be(dedent('''\
            Usage: trash-put [OPTION]... FILE...

            trash-put: error: no such option: --wrong-option
            '''))
        self.stdout_should_be('')
        assert_equals(2, self.exit_code)

def assert_line_in_text(expected_line, text):
    assert_in(expected_line, text.splitlines(),
                'Line not found in text\n'
                'line: %s\n' % expected_line +
                'text:\n%s\n' % format(text.splitlines()))

class TestTrashPutCmd(TrashPutTest):

    def test_on_help_option_print_help(self):
        self.run('--help')
        self.stdout_should_be(dedent('''\
            Usage: trash-put [OPTION]... FILE...

            Put files in trash

            Options:
              --version             show program's version number and exit
              -h, --help            show this help message and exit
              -d, --directory       ignored (for GNU rm compatibility)
              -f, --force           ignored (for GNU rm compatibility)
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
        self.run('.')
        self.stderr_should_be("trash-put: cannot trash directory '.'\n")

    def test_it_should_skip_dotdot_entry(self):
        self.run('..')
        self.stderr_should_be("trash-put: cannot trash directory '..'\n")

    def test_it_should_print_usage_on_no_argument(self):
        self.run()
        self.stderr_should_be(
            'Usage: trash-put [OPTION]... FILE...\n'
            '\n'
            'trash-put: error: Please specify the files to trash.\n')
        self.stdout_should_be('')

