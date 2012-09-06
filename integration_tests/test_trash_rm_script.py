from nose.tools import istest, assert_equals, assert_in
import subprocess
from subprocess import STDOUT, PIPE, check_output, call, Popen
from assert_equals_with_unidiff import assert_equals_with_unidiff as assert_equals
from textwrap import dedent

from pprint import pprint

@istest
class WhenNoArgs:
    def setUp(self):
        process = Popen(['python', 'trashcli/rm.py'],
                    env={'PYTHONPATH':'.'},
                    stdin=None,
                    stdout=PIPE,
                    stderr=PIPE)

        (self.stdout, self.stderr) = process.communicate()
        process.wait()
        self.returncode = process.returncode

    def test_should_print_usage_on_standard_error(self):
        assert_in("Usage:", self.stderr.splitlines())






