import os
import subprocess

from trashcli import base_dir


def run_command(cwd, command, args=None, input=''):
    class Result:
        def __init__(self, stdout, stderr):
            self.stdout = stdout
            self.stderr = stderr

    if args == None:
        args = []
    command_full_path = os.path.join(base_dir, command)
    process = subprocess.Popen(["python", command_full_path] + args,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, cwd=cwd)
    stdout, stderr = process.communicate(input=input.encode('utf-8'))

    return Result(stdout.decode('utf-8'), stderr.decode('utf-8'))

