import os
import subprocess
import sys
from setup import script_path_for
from trashcli import base_dir


def run_command(cwd, command, args=None, input='', env=None):
    class Result:
        def __init__(self, stdout, stderr, exit_code):
            self.stdout = stdout
            self.stderr = stderr
            self.exit_code = exit_code
            self.all = [stdout, stderr, exit_code]
        def __str__(self):
            return str(self.all)

    if env == None:
        env = {}
    if args == None:
        args = []
    command_full_path = script_path_for(command)
    env['PYTHONPATH'] = base_dir
    process = subprocess.Popen([sys.executable, command_full_path] + args,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=cwd,
                               env=merge_dicts(os.environ, env))
    stdout, stderr = process.communicate(input=input.encode('utf-8'))

    return Result(stdout.decode('utf-8'),
                  stderr.decode('utf-8'),
                  process.returncode)


def normalize_options(help_message):
    return help_message.replace('optional arguments', 'options')


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def last_line_of(stdout):
    if len(stdout.splitlines()) > 0:
        return stdout.splitlines()[-1]
    else:
        return ''


def first_line_of(out):
    return out.splitlines()[0]