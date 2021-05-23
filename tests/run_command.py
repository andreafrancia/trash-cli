import os
import subprocess

from trashcli import base_dir


def run_command(cwd, command, args=None, input=''):
    class Result:
        def __init__(self, stdout, stderr, exit_code):
            self.stdout = stdout
            self.stderr = stderr
            self.exit_code = exit_code

    if args == None:
        args = []
    command_full_path = os.path.join(base_dir, command)
    process = subprocess.Popen(["python", command_full_path] + args,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, cwd=cwd)
    stdout, stderr = process.communicate(input=input.encode('utf-8'))

    return Result(stdout.decode('utf-8'),
                  stderr.decode('utf-8'),
                  process.returncode)


def last_line_of(stdout):
    if len(stdout.splitlines()) > 0:
        return stdout.splitlines()[-1]
    else:
        return ''

def first_line_of(out):
    return out.splitlines()[0]