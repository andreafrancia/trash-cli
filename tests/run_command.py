import os
import subprocess
import sys

from scripts.make_scripts import script_path_for
from trashcli import base_dir


class CmdResult:
    def __init__(self, stdout, stderr, exit_code):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.all = [stdout, stderr, exit_code]

    def __str__(self):
        return str(self.all)

    def output(self):
        return self._format([self.stdout, self.stderr])

    def last_line_of_stderr(self):
        return last_line_of(self.stderr)

    def last_line_of_stdout(self):
        return last_line_of(self.stdout)

    @staticmethod
    def _format(outs):
        outs = [out for out in outs if out != ""]
        return "".join([out.rstrip("\n") + "\n" for out in outs])


def run_command(cwd, command, args=None, input='', env=None):
    if env is None:
        env = {}
    if args is None:
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

    return CmdResult(stdout.decode('utf-8'),
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
