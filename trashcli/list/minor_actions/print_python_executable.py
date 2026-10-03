from __future__ import print_function

from trashcli.lib.action import Action


class PrintPythonExecutableArgs:
    pass


class PrintPythonExecutable(Action):
    def __init__(self, out):
        self.out = out

    def run_action(self,
                   args,  # type: PrintPythonExecutableArgs
                   ):
        import sys
        print(sys.executable, file=self.out)
