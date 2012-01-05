# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import istest
from StringIO import StringIO
from trashcli.trash import TrashPutCmd
from integration_tests.assert_equals_with_unidiff import assert_equals_with_unidiff

@istest
class describe_TrashPutCmd:

    @istest
    def on_help_option_print_help(self):
        self.run('--help')
        self.stdout_should_be('''\
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
''')

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

    def run(self, *arg):
        self.stderr=StringIO()
        self.stdout=StringIO()
        args=['trash-put'] + list(arg)
        cmd=TrashPutCmd(self.stdout, self.stderr)
        self.detect_and_save_exit_code(lambda:cmd.run(args))

    def detect_and_save_exit_code(self, main_function):
        self.actual_exit_code=0
        try:
            result=main_function()
            if result is not None:
                self.actual_exit_code=result
        except SystemExit, e:
            self.actual_exit_code=e.code

    def stderr_should_be(self, expected_err):
        assert_equals_with_unidiff(expected_err, self.actual_stderr())

    def stdout_should_be(self, expected_out):
        assert_equals_with_unidiff(expected_out, self.actual_stdout())

    def actual_stderr(self):
        return self.stderr.getvalue()

    def actual_stdout(self):
        return self.stdout.getvalue()

