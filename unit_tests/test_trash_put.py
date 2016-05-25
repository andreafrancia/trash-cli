# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.put import TrashPutCmd

from nose.tools import istest, assert_in, assert_equal

# Try Python 2 import; if ImportError occurs, use Python 3 import
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from integration_tests.assert_equals_with_unidiff import assert_equals_with_unidiff
from textwrap import dedent

class TrashPutTest:
    def run(self, *arg):
        self.stderr = StringIO()
        self.stdout = StringIO()
        args = ['trash-put'] + list(arg)
        cmd = TrashPutCmd(self.stdout, self.stderr)
        self._collect_exit_code(lambda:cmd.run(args))

    def _collect_exit_code(self, main_function):
        self.exit_code = 0
        try:
            result=main_function()
            if result is not None:
                self.exit_code=result
        except SystemExit as e:
            self.exit_code = e.code

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
        assert_equal(2, self.exit_code)


def assert_line_in_text(expected_line, text):
    assert_in(expected_line, text.splitlines(),
                'Line not found in text\n'
                'line: %s\n' % expected_line +
                'text:\n%s\n' % format(text.splitlines()))

@istest
class describe_TrashPutCmd(TrashPutTest):

    @istest
    def on_help_option_print_help(self):
        self.run('--help')
        self.stdout_should_be(dedent('''\
            Usage: trash-put [OPTION]... FILE...

            Put files in trash

            Options:
              --version            show program's version number and exit
              -h, --help           show this help message and exit
              -d, --directory      ignored (for GNU rm compatibility)
              -f, --force          ignored (for GNU rm compatibility)
              -i, --interactive    ignored (for GNU rm compatibility)
              -r, -R, --recursive  ignored (for GNU rm compatibility)
              -v, --verbose        explain what is being done

            To remove a file whose name starts with a `-', for example `-foo',
            use one of these commands:

                trash -- -foo

                trash ./-foo

            Report bugs to http://code.google.com/p/trash-cli/issues
            '''))

    @istest
    def it_should_skip_dot_entry(self):
        self.run('.')
        self.stderr_should_be("trash-put: cannot trash directory `.'\n")

    @istest
    def it_should_skip_dotdot_entry(self):
        self.run('..')
        self.stderr_should_be("trash-put: cannot trash directory `..'\n")

    @istest
    def it_should_print_usage_on_no_argument(self):
        self.run()
        self.stderr_should_be(
            'Usage: trash-put [OPTION]... FILE...\n'
            '\n'
            'trash-put: error: Please specify the files to trash.\n')
        self.stdout_should_be('')


