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
    process = subprocess.Popen([sys.executable, command_full_path] + args,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=cwd,
                               env=merge_dicts(os.environ, env))
    stdout, stderr = process.communicate(input=input.encode('utf-8'))

    return CmdResult(stdout.decode('utf-8'),
                     stderr.decode('utf-8'),
                     process.returncode)
