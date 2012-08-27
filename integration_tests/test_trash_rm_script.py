from nose.tools import istest, assert_equals
import subprocess
from subprocess import STDOUT, PIPE, check_output, call, Popen

from pprint import pprint

@istest
class WhenNoArgs:
    def test_print_usage(self):
        process = Popen(['python', 'trashcli/rm.py'],
                    stdin=None,
                    stdout=PIPE,
                    stderr=PIPE)

        (stdout, stderr) = process.communicate()

        process.wait()

        result = dict()
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['returncode'] = process.returncode


