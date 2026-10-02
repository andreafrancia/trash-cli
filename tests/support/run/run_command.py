import os
import subprocess
import sys

from tests.support.dicts import merge_dicts
from tests.support.make_scripts import script_path_for
from tests.support.project_root import project_root
from tests.support.run.cmd_result import CmdResult


def run_command(cwd, command, args=None, input='', env=None):
    if env is None:
        env = {}
    if args is None:
        args = []
    command_full_path = script_path_for(command)
    env['PYTHONPATH'] = project_root()
    child_env = merge_dicts(os.environ, NO_COLORS, env)
    process = subprocess.Popen([sys.executable, command_full_path] + args,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=cwd,
                               env=child_env)
    stdout, stderr = process.communicate(input=input.encode('utf-8'))

    return CmdResult(stdout.decode('utf-8'),
                     stderr.decode('utf-8'),
                     process.returncode)


# Python 3.14 argparse colors the help and the usage messages when FORCE_COLOR
# is set, and the tests that compare that output need plain text.
#
# Both variables are set on purpose, each one switches the colors off by
# itself and each one takes precedence over FORCE_COLOR:
#  - NO_COLOR is the standard variable: it works for any program that the
#    command may run, not only for Python;
#  - PYTHON_COLORS=0 is the Python specific one (3.13+): it keeps working if
#    NO_COLOR is ignored or removed, e.g. by a wrapper or an env cleanup.
NO_COLORS = {'NO_COLOR': '1', 'PYTHON_COLORS': '0'}
